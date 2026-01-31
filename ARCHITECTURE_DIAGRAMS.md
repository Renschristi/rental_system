"""
SYSTEM ARCHITECTURE DIAGRAMS
=============================

This document provides visual representations of the system architecture,
data flows, and business processes.


1. APPLICATION ARCHITECTURE
============================

┌─────────────────────────────────────────────────────────────┐
│                     RENTAL MANAGEMENT SYSTEM                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐          ┌────▼────┐
   │ Customer│           │ Vendor  │          │  Admin  │
   └────┬────┘           └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │          Django Application Layer          │
        └─────────────────────┬─────────────────────┘
                              │
    ┌─────────┬───────────────┼───────────────┬─────────┐
    │         │               │               │         │
┌───▼───┐ ┌──▼──┐ ┌──────────▼──────────┐ ┌──▼───┐ ┌──▼────────┐
│Accounts│ │Prods│ │Rentals (CORE LOGIC)│ │Billing│ │Dashboards│
└───┬───┘ └──┬──┘ └──────────┬──────────┘ └──┬───┘ └──┬────────┘
    │        │               │               │        │
    └────────┴───────────────┴───────────────┴────────┘
                              │
                    ┌─────────▼─────────┐
                    │  PostgreSQL DB    │
                    └───────────────────┘


2. DATA MODEL RELATIONSHIPS
============================

User (Custom Auth)
  │
  ├─1:N─→ Product (as vendor)
  ├─1:N─→ Quotation (as customer)
  ├─1:N─→ RentalOrder (as customer)
  └─1:N─→ Invoice (as customer)

Product
  │
  ├─N:1─→ Category
  ├─N:1─→ User (vendor)
  ├─1:N─→ QuotationLine
  └─1:N─→ RentalOrderLine ⭐ (RESERVATION)

Quotation
  │
  ├─N:1─→ User (customer)
  ├─1:N─→ QuotationLine
  └─1:1─→ RentalOrder (on confirmation)

RentalOrder ⭐ CORE
  │
  ├─N:1─→ User (customer)
  ├─1:1─→ Quotation
  ├─1:N─→ RentalOrderLine (LOCKS INVENTORY)
  └─1:N─→ Invoice

Invoice
  │
  ├─N:1─→ RentalOrder
  ├─N:1─→ User (customer)
  └─1:N─→ Payment


3. RENTAL LIFECYCLE FLOW
=========================

   CUSTOMER JOURNEY                    SYSTEM STATE
   ────────────────                    ────────────

1. Browse Products
   │
   ├─→ Select Product & Dates
   │
   ├─→ Add to Quotation ────────────→ Quotation: DRAFT
   │                                   (Editable)
   │
2. Review Quotation
   │
   ├─→ Modify/Remove Items
   │
   └─→ Click "Confirm Order"
           │
           ▼
   ┌───────────────────────┐
   │ RESERVATION ALGORITHM │  ⭐ CRITICAL
   │ - Lock products       │
   │ - Check availability  │
   │ - All or nothing      │
   └───────────────────────┘
           │
           ├─→ Available? ──NO──→ Error: "Not available"
           │
           └─→ Yes
               │
               ├─→ Create RentalOrder ──────→ RentalOrder: CONFIRMED
               │                              (Inventory LOCKED)
               │
               ├─→ Generate Invoice ────────→ Invoice: DRAFT
               │
               └─→ Confirmation Email

3. Pay Invoice
   │
   ├─→ Make Payment ────────────────→ Payment created
   │                                  Invoice: PARTIAL/PAID
   │
4. Pickup
   │
   └─→ Vendor marks pickup ─────────→ RentalOrder: ACTIVE
                                       (Product with customer)

5. Return
   │
   ├─→ Vendor processes return
   │
   ├─→ Check return date
   │
   ├─→ Late? ──YES──→ Calculate late fee
   │                  Update invoice
   │
   └─→ Mark as returned ────────────→ RentalOrder: RETURNED
                                       (Inventory RELEASED)


4. RESERVATION ALGORITHM FLOWCHART
==================================

START: User clicks "Confirm Quotation"
   │
   ▼
[Lock Quotation Row]
   │
   ▼
FOR EACH item in quotation:
   │
   ├─→ [Lock Product Row]
   │
   ├─→ [Find Overlapping Rentals]
   │    │
   │    └─→ Query: WHERE start_date < end_date
   │                AND   end_date > start_date
   │                AND   status IN ('CONFIRMED', 'ACTIVE')
   │
   ├─→ [Sum Reserved Quantities]
   │
   ├─→ [Calculate Available]
   │    Available = Product.quantity - Reserved
   │
   └─→ Available >= Requested?
       │
       ├─NO──→ Add to unavailable_items[]
       │
       └─YES──→ Continue to next item

   ▼
Any items unavailable?
   │
   ├─YES──→ [Rollback Transaction]
   │        │
   │        └─→ Show Error Message
   │            END (FAILURE)
   │
   └─NO────→ [Create RentalOrder]
             │
             ├─→ [Create RentalOrderLines] ⭐ LOCKS INVENTORY
             │
             ├─→ [Update Quotation Status]
             │
             ├─→ [Generate Invoice]
             │
             ├─→ [Commit Transaction]
             │
             └─→ Show Success Message
                 END (SUCCESS)


5. DATABASE LOCKING STRATEGY
=============================

Concurrent Access Scenario:

Time    User A              Database            User B
────    ──────              ────────            ──────
T1      Confirm order
         │
T2       └─→ SELECT...      Lock Row           Confirm order
             FOR UPDATE      (Product #1)        │
                                                 │
T3      Check availability                       └─→ SELECT...
        (reads locked data)                          FOR UPDATE
                                                     │
T4      Available: 1                                 WAIT ⏸
        (OK to proceed)                              (blocked)
         │
T5       └─→ INSERT         Create
             RentalOrderLine Reservation
                            
T6      COMMIT               Release Lock
        Transaction          ✓
         │
T7       │                                       Continue ▶
         │                                       Check availability
         │                                       (reads updated data)
         │
T8       │                                       Available: 0
         │                                       (NOT OK)
         │
T9       │                                       ROLLBACK
         │                                       Show error
         │
END     ✓ SUCCESS                                ✗ REJECTED

Result: No double booking! One succeeds, one fails gracefully.


6. INVENTORY STATE TRANSITIONS
===============================

Product: MacBook Pro
Quantity: 1

STATE 1: Available
───────────────────
Jan ├─────────────────────────────────────┤
    1    5    10   15   20   25   30

Quantity Available: 1
Status: Ready to rent


STATE 2: Reserved (Rental A confirmed)
───────────────────────────────────────
Jan ├─────────────────────────────────────┤
    1 [═══A═══] 10   15   20   25   30
      Jan 1-7

Quantity Available: 0 (for Jan 1-7)
Quantity Available: 1 (for Jan 8+)


STATE 3: Active (Rental A picked up)
─────────────────────────────────────
Jan ├─────────────────────────────────────┤
    1 [▓▓▓A▓▓▓] 10   15   20   25   30
      Jan 1-7   (with customer)

Quantity Available: 0 (for Jan 1-7)
Still locked


STATE 4: Returned (Rental A completed)
───────────────────────────────────────
Jan ├─────────────────────────────────────┤
    1    5    10   15   20   25   30

Quantity Available: 1 (for all dates)
Inventory released ✓


7. OVERLAP DETECTION LOGIC
===========================

Case 1: Complete Overlap (REJECT)
──────────────────────────────────
Existing:  ├───────────┤
           10         20

New:          ├───────────┤
              15         25

Overlap: start1 < end2 (10 < 25) ✓
         end1 > start2 (20 > 15) ✓
Result: OVERLAP DETECTED ✗


Case 2: Contained (REJECT)
───────────────────────────
Existing:  ├──────────────────────┤
           10                    30

New:          ├─────┤
              15   20

Overlap: start1 < end2 (10 < 20) ✓
         end1 > start2 (30 > 15) ✓
Result: OVERLAP DETECTED ✗


Case 3: Adjacent (ALLOW)
─────────────────────────
Existing:  ├───────────┤
           10         20

New:                   ├───────────┤
                       20         30

Overlap: start1 < end2 (10 < 30) ✓
         end1 > start2 (20 > 20) ✗
Result: NO OVERLAP ✓


Case 4: Separate (ALLOW)
─────────────────────────
Existing:  ├───────────┤
           10         20

New:                      ├───────────┤
                          25         35

Overlap: start1 < end2 (10 < 35) ✓
         end1 > start2 (20 > 25) ✗
Result: NO OVERLAP ✓


8. USER ROLE PERMISSIONS
=========================

                Customer    Vendor      Admin
                ────────    ──────      ─────
Browse Products    ✓          ✓           ✓
Add to Cart        ✓          ✗           ✗
Confirm Order      ✓          ✗           ✗
View Own Rentals   ✓          ✗           ✓
Pay Invoices       ✓          ✗           ✗

Manage Products    ✗          ✓           ✓
Process Pickup     ✗          ✓           ✓
Process Return     ✗          ✓           ✓
View Earnings      ✗          ✓           ✓

Admin Panel        ✗          ✗           ✓
System Analytics   ✗          ✗           ✓
User Management    ✗          ✗           ✓
Global Reports     ✗          ✗           ✓


9. PAYMENT FLOW
===============

Invoice Created
   │
   ├─→ Status: DRAFT
   │   Amount: $100
   │   Paid: $0
   │   Balance: $100
   │
   ▼
Customer Makes Payment #1
   │
   ├─→ Pay: $60
   │
   ├─→ Status: PARTIAL
   │   Amount: $100
   │   Paid: $60
   │   Balance: $40
   │
   ▼
Customer Makes Payment #2
   │
   ├─→ Pay: $40
   │
   └─→ Status: PAID
       Amount: $100
       Paid: $100
       Balance: $0 ✓


10. LATE FEE CALCULATION
========================

Rental Details:
- Product: Laptop
- Daily Rate: $50
- Quantity: 1
- Planned End: Jan 10
- Actual Return: Jan 13
- Late Days: 3
- Late Fee Rate: 10%

Calculation:
Late Fee = Daily Rate × Quantity × Days Late × Rate
         = $50 × 1 × 3 × 0.10
         = $15

Invoice Update:
Original Total: $500
Late Fee: +$15
New Total: $515


LEGEND
======
⭐ = Critical component
✓ = Success/Allowed
✗ = Failure/Rejected
─ = Timeline
├ = Connection
│ = Flow
▼ = Direction
[═] = Reserved period
[▓] = Active rental
"""
