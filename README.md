Solution:

Gaol 1:
As i wasnt sure whether we wanted to have mutiple endpoint depicting different types of orders (ie: cancelled, active, all) i opted to keep eveything in one location for simplicity for now. 
- I have added 2 new fields to the order table.
- the view is now a modelviewset rather than read only which then allowed me to update the serialzer from a detailed view for cancelled orders.
- Validation checks in the serializser have been put in to ensure that the order is only being cancelled and nothing else about the other is changing.
- Validation checks in the model to check for if the order can be cancelled.

Goal 2:
- a method get_number_of_orders_and_cancellation_rate() was added to the orders table to return the number of orders, cancellation rate and event as a dict

Goal 3:
- a Property method was added to the orders table
- all order objects that were cancelled were first gathered
- - it first determines the date of the first object in the queryset.
  - it then runs through the query set and
       -if date of the current order is the same as the date of the previous order then the current_quantity is incremented
       -if the dates are different then it checks to see if this new current_quantity is more than max_quantity(which is the variable that will hold the most cancellations so far)
          if this is true, max_quantity is reset to current_quantity, and a new max date is set which holds the date of the most cancellations
    -at the end of the loop, there is a final check for the last value in the queryset to check if this has exceeded the current max_quantity. if so it adjusts accordingly.

  -returns a dict with the date and the number of cancelled tickets

  
