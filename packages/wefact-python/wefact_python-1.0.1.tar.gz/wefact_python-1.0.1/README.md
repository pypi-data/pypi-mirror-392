# WeFact Python Wrapper

[![PyPI version](https://img.shields.io/pypi/v/wefact-python.svg)](https://pypi.org/project/wefact-python/)
[![Tests](https://github.com/zzinnovate/wefact-python/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/zzinnovate/wefact-python/actions/workflows/run-tests.yml)
[![codecov](https://codecov.io/gh/zzinnovate/wefact-python/graph/badge.svg?token=R08526JCXI)](https://codecov.io/gh/zzinnovate/wefact-python)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)

An unofficial, batteries-included Python client for the WeFact API. Pragmatic, typed where it counts, and intentionally minimal on magic.

**What is WeFact?** [WeFact](https://www.wefact.nl/) is a Dutch invoicing and accounting platform. Create invoices and quotes, process supplier invoices, and maintain real-time insight into your administration.

Maintained by [zzinnovate](https://github.com/zzinnovate). Open source, community-friendly, and actively maintained. Not affiliated with WeFact. For the upstream API, see the official [WeFact API documentation](https://www.wefact.nl/api/).

## Documentation

📖 **[View Full Documentation →](https://zzinnovate.github.io/wefact-python/)**

Complete guides and API reference:
- **Getting Started** - [Installation](https://zzinnovate.github.io/wefact-python/getting-started/installation/) • [Usage](https://zzinnovate.github.io/wefact-python/getting-started/usage/) • [Configuration](https://zzinnovate.github.io/wefact-python/getting-started/configuration/)
- **API Reference** - [Resources](https://zzinnovate.github.io/wefact-python/api/resources/) • [Parameters](https://zzinnovate.github.io/wefact-python/api/parameters/) • [Variables (Enums)](https://zzinnovate.github.io/wefact-python/api/variables/) • [Errors](https://zzinnovate.github.io/wefact-python/api/errors/)
- **Guides** - [Invoice Lifecycle](https://zzinnovate.github.io/wefact-python/guides/invoice-lifecycle/) • [CLI Testing Tool](https://zzinnovate.github.io/wefact-python/guides/cli-tool/)
- **Project** - [Contributing](https://zzinnovate.github.io/wefact-python/project/contributing/) • [Changelog](https://zzinnovate.github.io/wefact-python/project/changelog/) • [Security](https://zzinnovate.github.io/wefact-python/project/security/)

## Requirements

- Python 3.11+

## Install

```bash
# Basic installation (library only)
pip install wefact-python

# With CLI testing tool
pip install "wefact-python[cli]"

# For development (includes CLI, testing, and docs)
pip install -e ".[all]"
```

## Quick start

```python
import os
from wefact import WeFact

client = WeFact(api_key=os.getenv('WEFACT_API_KEY'))

# List your latest invoices
result = client.invoices.list(limit=25)
print(result)
```

## Features

- **Minimal dependencies** - Only `requests` for HTTP calls
- **Type hints** - Better IDE support and fewer runtime errors
- **Direct API mapping** - Mirrors WeFact's controller/action structure
- **Error handling** - Clear exceptions for common failure modes
- **Attachment support** - Base64 encoding/decoding utilities built-in
- **Production-tested** - Used by zzinnovate in client projects

## Resources

Complete coverage of all 13 WeFact API resources:

Invoices • Credit Invoices • Debtors • Products • Creditors • Groups • Subscriptions • Quotes • Interactions • Tasks • Transactions • Cost Categories • Settings

## Common operations

```python
# Show a debtor
debtor = client.debtors.show(Identifier="DB10000")

# Create an invoice
invoice = client.invoices.create(
    DebtorCode="DB10000",
    InvoiceLines=[
        {
            "Number": 1,
            "ProductCode": "P0001",
            "Description": "Service",
            "PriceExcl": 100
        }
    ],
)

# Mark invoice as paid
client.invoices.mark_as_paid(Identifier=invoice["invoice"]["Identifier"])
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and workflow guidelines.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities and best practices.

## Credits

- [Sjoerd Zaalberg van Zelst](https://github.com/sjoerdzzid) (zzinnovate)
- [All contributors](https://github.com/zzinnovate/wefact-python/graphs/contributors)
- Inspired by [vormkracht10/wefact-php](https://github.com/vormkracht10/wefact-php)

## License

MIT. See [LICENSE](LICENSE).