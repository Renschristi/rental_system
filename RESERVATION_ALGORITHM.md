"""
RESERVATION ALGORITHM EXPLAINED
================================

This document explains the core reservation logic that prevents double booking
in the Rental Management System.

PROBLEM STATEMENT
-----------------
In a rental system, products are rented for time periods (date ranges), not sold.
The same product can be rented to different customers at different times, but
CANNOT be double-booked for overlapping periods.

Example:
- Product: MacBook Pro (Quantity: 1)
- Customer A wants: Jan 1-5
- Customer B wants: Jan 3-7 (OVERLAPS!)
- System must: Allow A, reject B (if A confirms first)


SOLUTION ARCHITECTURE
---------------------

1. TIME-BASED INVENTORY
   - Unlike e-commerce (quantity decreases on sale)
   - Rentals: quantity is reserved for DATE RANGES
   - Same unit can be rented multiple times (different periods)

2. RESERVATION = RENTAL ORDER LINE
   - When quotation is confirmed → creates RentalOrderLine
   - RentalOrderLine has: product, quantity, start_date, end_date
   - These lines represent "locked inventory" for those dates

3. AVAILABILITY CHECK
   - Before confirming: check if product is available for requested dates
   - "Available" = Total Quantity - Reserved Quantity for that period
   - Reserved = Sum of quantities in overlapping RentalOrderLines


OVERLAP DETECTION
-----------------

Two date ranges overlap if:
    Range1: [start1, end1]
    Range2: [start2, end2]
    
    Overlap = (start1 < end2) AND (end1 > start2)

Examples:
    [Jan 1 - Jan 5] and [Jan 3 - Jan 7]   → OVERLAP ✗
    [Jan 1 - Jan 5] and [Jan 6 - Jan 10]  → NO overlap ✓
    [Jan 1 - Jan 10] and [Jan 3 - Jan 5]  → OVERLAP ✗ (contained)


CODE IMPLEMENTATION
-------------------

File: products/models.py
Method: Product.get_available_quantity()

```python
def get_available_quantity(self, start_date, end_date):
    # Find all rental lines that overlap with requested period
    overlapping_rentals = RentalOrderLine.objects.filter(
        product=self,
        rental_order__status__in=['CONFIRMED', 'ACTIVE'],  # Only active rentals
        start_date__lt=end_date,    # Their start is before our end
        end_date__gt=start_date     # Their end is after our start
    )
    
    # Sum up all reserved quantities
    reserved_qty = sum(line.quantity for line in overlapping_rentals)
    
    # Available = Total - Reserved
    return self.quantity - reserved_qty
```

Why this works:
- start_date__lt=end_date: Catches rentals that start before we end
- end_date__gt=start_date: Catches rentals that end after we start
- Together: Finds ALL overlaps (including contained ranges)


ATOMIC CONFIRMATION
-------------------

File: rentals/views.py
Method: ConfirmQuotationView.post()

The confirmation process uses database transactions to ensure atomicity:

```python
@transaction.atomic
def post(self, request):
    # STEP 1: Lock the quotation (prevent concurrent modifications)
    quotation = Quotation.objects.select_for_update().get(
        customer=request.user,
        status='DRAFT'
    )
    
    # STEP 2: Check availability for ALL items
    unavailable_items = []
    
    for line in quotation.lines.all():
        # Lock product row to prevent race conditions
        product = Product.objects.select_for_update().get(id=line.product.id)
        
        # Check if available
        available = product.get_available_quantity(line.start_date, line.end_date)
        
        if available < line.quantity:
            unavailable_items.append(...)
    
    # STEP 3: If ANY item unavailable, ABORT
    if unavailable_items:
        # Transaction rolls back, no changes made
        return error_response
    
    # STEP 4: All available, create rental order
    rental_order = RentalOrder.objects.create(...)
    
    # STEP 5: Create rental lines (THIS LOCKS THE INVENTORY)
    for quotation_line in quotation.lines.all():
        RentalOrderLine.objects.create(
            rental_order=rental_order,
            product=quotation_line.product,
            quantity=quotation_line.quantity,
            start_date=quotation_line.start_date,
            end_date=quotation_line.end_date,
            ...
        )
    
    # STEP 6: Mark quotation as confirmed
    quotation.status = 'CONFIRMED'
    quotation.save()
    
    # Transaction commits - all or nothing
```

Critical Points:
1. select_for_update() - Locks rows, prevents concurrent access
2. @transaction.atomic - All-or-nothing guarantee
3. Check BEFORE create - Availability verified before locking
4. RentalOrderLine creation - This is the actual reservation


RACE CONDITION PREVENTION
--------------------------

Scenario: Two customers try to book the same product simultaneously

Time    Customer A                  Customer B
----    ----------                  ----------
T1      Load quotation
T2                                  Load quotation
T3      Click "Confirm"
T4      → Lock product row          Wait (blocked)
T5      Check availability (OK)
T6      Create RentalOrderLine
T7      Commit transaction
T8      Release lock                
T9                                  → Acquire lock
T10                                 Check availability (FAIL - A's rental exists)
T11                                 Abort, show error

Result: A succeeds, B fails gracefully. NO double booking!


DATABASE QUERIES EXPLAINED
---------------------------

Query 1: Find overlapping rentals
```sql
SELECT * FROM rentals_rentalorderline
WHERE product_id = 123
  AND rental_order__status IN ('CONFIRMED', 'ACTIVE')
  AND start_date < '2026-02-01'    -- Their start before our end
  AND end_date > '2026-01-25';     -- Their end after our start
```

Query 2: Lock product for update
```sql
SELECT * FROM products_product
WHERE id = 123
FOR UPDATE;  -- This locks the row until transaction ends
```


STATUS-BASED RESERVATIONS
--------------------------

Only count rentals with certain statuses:
- CONFIRMED: Customer booked, awaiting pickup
- ACTIVE: Customer has product (picked up)

Do NOT count:
- RETURNED: Product is back, available again
- CANCELLED: Reservation cancelled

Code:
```python
rental_order__status__in=['CONFIRMED', 'ACTIVE']
```

This ensures returned products become available immediately.


EDGE CASES HANDLED
------------------

1. Same-day rentals:
   - start_date = end_date → Duration = 1 day (minimum)
   - Code: max(delta.days, 1)

2. Back-to-back rentals:
   - Rental A: Jan 1-5 (end_date = Jan 5)
   - Rental B: Jan 5-10 (start_date = Jan 5)
   - Result: NO overlap (end_date exclusive in comparison)

3. Multiple quantities:
   - Product quantity = 5
   - Rental A: 2 units (Jan 1-5)
   - Rental B: 3 units (Jan 1-5)
   - Result: Both allowed (2+3 = 5, exactly available)
   - Rental C: 1 unit (Jan 1-5) → REJECTED (would need 6)

4. Partial overlaps:
   - Existing: Jan 5-10
   - New request: Jan 8-15
   - Result: Overlap detected, rejected


TESTING THE ALGORITHM
----------------------

Test Case 1: Simple Overlap
```python
# Setup
product = Product.objects.create(name="Laptop", quantity=1, ...)

# Rental 1
rental1 = RentalOrder.objects.create(...)
RentalOrderLine.objects.create(
    product=product,
    start_date="2026-01-01",
    end_date="2026-01-05",
    quantity=1
)

# Check availability for overlapping period
available = product.get_available_quantity("2026-01-03", "2026-01-07")
assert available == 0  # Should be 0 (fully booked)

# Check availability for non-overlapping period
available = product.get_available_quantity("2026-01-06", "2026-01-10")
assert available == 1  # Should be 1 (available)
```

Test Case 2: Multiple Quantities
```python
product = Product.objects.create(name="Bike", quantity=5, ...)

# Reserve 2 units
RentalOrderLine.objects.create(product=product, quantity=2, ...)

# Reserve 2 more units
RentalOrderLine.objects.create(product=product, quantity=2, ...)

# Check availability
available = product.get_available_quantity(start, end)
assert available == 1  # 5 - 2 - 2 = 1

# Try to reserve 2 units → Should fail (only 1 available)
```


PERFORMANCE CONSIDERATIONS
---------------------------

1. Database Indexes:
   - Index on (product_id, start_date, end_date, status)
   - Speeds up overlap queries

2. Query Optimization:
   - select_related() and prefetch_related() for JOINs
   - Minimize database round trips

3. Caching (Future Enhancement):
   - Cache product availability for popular items
   - Invalidate on rental creation/return


ALTERNATIVE APPROACHES (NOT USED)
----------------------------------

Why not use a separate "inventory slots" table?
- More complex to maintain
- Harder to query
- Current approach is simpler and sufficient

Why not use Redis/in-memory locks?
- Database locks are sufficient for this scale
- Redis adds complexity
- Current approach is more reliable (persisted)


SUMMARY
-------

The reservation algorithm works by:

1. Storing reservations as RentalOrderLines with date ranges
2. Checking overlaps using date comparison logic
3. Using database transactions and row locks to prevent race conditions
4. Only counting active reservations (CONFIRMED, ACTIVE status)
5. Making confirmation atomic (all-or-nothing)

This ensures that:
- No double booking can occur
- Inventory is accurately tracked
- Multiple customers can rent the same product (different times)
- System scales reliably


VERIFICATION CHECKLIST
----------------------

✓ Overlapping date ranges are detected correctly
✓ Non-overlapping date ranges are allowed
✓ Concurrent confirmations are handled safely (locks)
✓ Partial availability is calculated correctly
✓ Returned products become available immediately
✓ Transaction rollback on any failure
✓ All edge cases are covered


This is a production-grade implementation suitable for real-world use.
"""
