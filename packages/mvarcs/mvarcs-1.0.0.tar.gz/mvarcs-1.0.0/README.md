# mvarcs: Python Mark Verifying Authority Root Certificates

mvarcs provides a collection of Root Certificates for validating
the trustworthiness of Mark Certificates such as Verified Mark
Certificates (VMC) and Common Mark Certificates (CMC) used in BIMI
(Brand Indicators for Message Identification).

## Installation

``mvarcs`` is available on PyPI. Simply install it with ``pip``:

``` sh
python -m pip install mvarcs
```

## Usage

To reference the installed certificate authority (CA) bundle, you can use the
built-in function:

``` py
import mvarcs
mvarcs.where()
# '/usr/local/lib/python3.13/site-packages/mvarcs/mvarcs/cacerts.pem'
```

Additionally, you can get the contents directly:

``` py
import mvarcs
mvarcs.contents()
# Issuer: ...
# ...
# -----END CERTIFICATE-----
```

Or from the command line:

``` sh
python -m mvarcs
# /usr/local/lib/python3.13/site-packages/mvarcs/mvarcs/cacert.pem

python -m mvarcs -c
# Issuer: ...
# ...
# -----END CERTIFICATE-----
```

## Addition/Removal of Certificates

See <https://github.com/markcerts/mvarcs>
