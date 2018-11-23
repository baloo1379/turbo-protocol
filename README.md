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
    * `100` `4` - modulo
    * `101` `5` - power
    * `110` `6` - logarithm 
    * `111` `7` - absolute and factorial (first argument absolute, second factorial)

2. Status field - 4-bit field containing the transmission status.
    * `0001` `1` - a query
    * `0010` `2` - the result of the operation
    * `0011` `3` - general error
    * `0100` `4` - error - the result is too big
    * `0101` `5` - error - wrong status
    * `0110` `6` - error - factorial too big
    * `0111` `7` - error - division by 0
    * `1000` `8` - error - wrong logarithm base or argument

3. Data length field - a 32-bit field containing information about the length of the data field.
4. Data field - the field where the information is located:
    * session number field - 32 bits
    * field of the first argument - 32 bits
    * field of the second argument - 32 bits
    
## Structure of protocol

| offset | length (bits) | field |
|:---:|:---:|:--------:|
|  0  |   3 | operation|
|  3  |   4 | status |
|  7  |  32 | length |
|  39 |  32 | session id|
|  71 |  32 | first argument|
| 104 |  32 | second argument|
| 136 |   1 | offset |



