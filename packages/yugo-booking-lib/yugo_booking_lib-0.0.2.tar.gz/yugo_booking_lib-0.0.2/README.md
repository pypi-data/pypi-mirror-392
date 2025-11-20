# yugo-booking-lib

`yugo-booking-lib` is a small Python library used in the **Yugo
Accommodation** project.

It provides a `BookingPrice` class that helps calculate:
- number of nights between check-in and check-out dates
- total booking price including optional tax and a fixed fee

This library is used inside the Django `book_room` view to compute the
final room cost before confirming the booking.
