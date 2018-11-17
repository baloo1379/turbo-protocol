# turbo-protocol
Simple protocol for CS studies on PUT

Features:
* connection-oriented,
* all data sent in binary form,
* 3-bit operation field,
* 4-bit status field,
* 32-bit data length field,
* variable-size data field,
* additional fields defined by the programmer, nested in the data field.

1. Operation field - 3-bit field containing information on one of 9 mathematical operations.
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
    * `0010` `2` - the result of the operation
    * `0011` `3` - general error
    * `0100` `4` - error - the result is too big
    * `0101` `5` - error - wrong status

3. Data length field - a 32-bit field containing information about the length of the data field.
4. Data field - the field where the information is located:
    * session number field - 32 bits
    * field of the first argument - 32 bits
    * field of the second argument - 32 bits
    
## Header

|0-2|3-6|7-38|39|
|:----:|:-----:|:-----:|:-----:|
|operation|status|length|offset|

## Data

| 0-31 |
|:----:|
|session id|
|first argument|
|second argument|


