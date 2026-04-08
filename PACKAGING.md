# SysGuard Packaging

## Build the native app

Run:

```bash
./build_sysguard_app.command
```

This generates a native macOS app bundle at `SysGuard.app`.

## Build the release DMG

Run:

```bash
./build_release.command
```

This will:

1. Generate visual assets
2. Build the native `SysGuard.app`
3. Ad-hoc sign the app
4. Build `release/SysGuard-7.4-macOS.dmg`

## Storage location

When the packaged app runs, SysGuard stores its runtime data in:

`~/Library/Application Support/SysGuard`

## Notes

- The DMG includes `SysGuard.app`, an `Applications` shortcut, and a short install guide.
- The app is ad-hoc signed for local distribution and testing.
- For public distribution outside your own machine, notarization is still recommended.
