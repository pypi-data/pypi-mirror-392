# openocd

Python interface library for [OpenOCD](https://openocd.org/).


## Dependencies

* Python >= 3.10
* typing_extensions >= 4.5.0


## Installation

Prerequisites:

* Python 3.10 or higher

  * https://www.python.org/

* setuptools

  * https://pypi.org/project/setuptools/

To install this package, run:

```bash
python setup.py install
```


## Example

```python
from openocd import OpenOcd

with OpenOcd() as oocd:
    oocd.halt()
    registers = oocd.read_registers(['pc', 'sp'])

    print('Program counter: 0x%x' % registers['pc'])
    print('Stack pointer: 0x%x' % registers['sp'])

    oocd.resume()
```

## Support

If you appreciate the project, feel free to donate on Liberapay:

[![Liberapay donation link](https://liberapay.com/assets/widgets/donate.svg)](https://liberapay.com/zapb/donate)

## License

This project is licensed under the terms of the GNU Lesser General Public License (LGPL) v2.1 or later.
See [LICENSE](LICENSE) file for details.
