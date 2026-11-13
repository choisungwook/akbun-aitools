# Policies

* [Plugin versioning](plugin-versioning.md) - Changing a skill or agent under plugins/ bumps that plugin's version once, from origin/main
* [README skill index](readme-index.md) - Adding or removing a skill updates the README plugin table in the same change
* [Image work](image-work.md) - From reference images extract only the style; never copy subjects, scenes or text
* [Verification](verification.md) - Run the checks matching the changed paths while editing and put commands and output in the PR verification table
* [Risk tiers](risk-tiers.md) - Changed paths set the PR risk tier; agents never merge high-tier PRs
* [Pull request format](pull-request.md) - PR body has three H1s (구현, 검증, 리스크), Korean bullet style, at most 40 lines
