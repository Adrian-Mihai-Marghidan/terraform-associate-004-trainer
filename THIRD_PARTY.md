# Upstream references and licenses

The mentor's original scripts, instructions, and teaching material use the [MIT license](LICENSE). The independently maintained simulator has its own source tree and license; a mentor checkout does not include or relicense it.

This repository links to official documentation and installs development tools into ignored local directories. It does not distribute Terraform, Go, or provider binaries. Upstream software, trademarks, and documentation retain their own terms:

| Reference or tool | Upstream source and terms |
| --- | --- |
| HashiCorp Terraform CLI | [Terraform source/license](https://github.com/hashicorp/terraform/blob/v1.12.2/LICENSE) |
| Go toolchain | [Go source/license](https://go.dev/LICENSE) |
| Simulator provider development | [Terraform Plugin Framework](https://github.com/hashicorp/terraform-plugin-framework), [HCL](https://github.com/hashicorp/hcl), and dependencies recorded in the simulator's go.mod/go.sum |
| Curriculum and exam references | [Official Terraform certification documentation](https://developer.hashicorp.com/certifications/terraform-associate); objective labels here are paraphrases |
| Codex runtime | [OpenAI Codex](https://developers.openai.com/codex); this repository supplies instructions and a skill, not the Codex application |
| CI checkout/runtime setup | [actions/checkout](https://github.com/actions/checkout), [actions/setup-python](https://github.com/actions/setup-python) |

Assessment items are original practice material. Do not contribute copied proprietary exam questions, book chapters, employer code/data, or dependencies whose terms conflict with the intended distribution.
If distributing tool/provider binaries later, review their upstream notices and release obligations separately from this source repository's MIT license.
