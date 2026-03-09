.PHONY: app install launch-agent unlaunch-agent clean

# Build the .app bundle via py2app
app:
	./scripts/build.sh

# Copy the built app to /Applications
install: app
	@echo "Installing MagicSpell.app to /Applications..."
	cp -r dist/MagicSpell.app /Applications/
	@echo "Done. Run with:  open /Applications/MagicSpell.app"

# Install the Launch Agent (run at login)
launch-agent:
	@python3 -c "from magicspell.launchd import install; install()"
	@echo "Launch Agent installed. MagicSpell will start on login."

# Uninstall the Launch Agent
unlaunch-agent:
	@python3 -c "from magicspell.launchd import uninstall; uninstall()"
	@echo "Launch Agent removed."

# Remove build artifacts
clean:
	./scripts/build.sh clean
	rm -rf .eggs *.egg-info
