# turbo-protocol
Simple protocol for CS studies on PUT

Features:
* connection,
* all data sent in binary form,
* 3 bits operation field,
* status field with a length of 4 bits,
* 32-bit data length field,
* variable-size data field,
* additional fields defined by the programmer, nested in the data field.

1. Operation field - 3-bit field containing information on one of 9 information.
    * `000` `0` - adding
    * `001` `1` - subtraction
    * `010` `2` - multiplication
    * `011` `3` - dividing
    * `100` `4` - OR
    * `101` `5` - XOR
    * `110` `6` - AND
    * `111` `7` - NOT and factorial (first argument NOT, second factorial)

2. Status field - 4-bit field containing the transmission status.
    * `0001` `1` - a query
    * `0010` `2` - the result of the action
    * `0011` `3` - the result of factorial
    * `0100` `4` - error - the result is too big
    * `0101` `5` - general error

3. Data length field - a 32-bit field containing information about the length of the data field.
4. Data field - the field where the information is located:
    * session number field - 32 bits
    * field of the first argument - 32 bits
    * field of the second argument - 32 bits