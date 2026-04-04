PLUGIN_DIR    := plugins/akbun-skills
SKILLS_DIR    := $(PLUGIN_DIR)/skills
AGENTS_DIR    := $(PLUGIN_DIR)/agents
PLUGIN_JSON   := $(PLUGIN_DIR)/.claude-plugin/plugin.json
MARKETPLACE   := .claude-plugin/marketplace.json

.PHONY: help list list-skills list-agents release

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  list          List all AI tools (skills + agents)"
	@echo "  list-skills   List available skills"
	@echo "  list-agents   List available subagents"
	@echo "  release V=x.y.z  Bump version in plugin.json"
	@echo ""
	@echo "Install via Claude Code:"
	@echo "  /plugin marketplace add choisungwook/akbun-aitools"
	@echo "  /plugin install akbun-skills@akbun-aitools"
	@echo ""
	@echo "Update (for users):"
	@echo "  claude plugin update akbun-skills@akbun-aitools"

list: list-skills list-agents

list-skills:
	@echo "[skills]"
	@ls $(SKILLS_DIR)

list-agents:
	@echo "[agents]"
	@ls $(AGENTS_DIR)

release:
ifndef V
	$(error V is required. Usage: make release V=x.y.z)
endif
	@current=$$(jq -r '.version' $(PLUGIN_JSON)); \
	echo "$$current -> $(V)"; \
	tmp=$$(mktemp); \
	jq --arg v "$(V)" '.version = $$v' $(PLUGIN_JSON) > $$tmp && mv $$tmp $(PLUGIN_JSON); \
	echo "Updated $(PLUGIN_JSON) to $(V)"; \
	echo "Next: git commit -m 'release: v$(V)' && git push"
