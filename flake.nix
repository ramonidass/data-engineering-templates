{
  description = "Dev shell for working on the data engineering templates.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs = { self, nixpkgs, }:
    let
      allSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs allSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      devShells = forAllSystems ({ pkgs }: {
        default = pkgs.mkShell {
          packages = (with pkgs; [
            just
            copier
            git-secrets
            pre-commit
            shellcheck
          ]);
          shellHook = ''
            mkdir -p "$PWD/.direnv/cache"
            export XDG_CACHE_HOME="$PWD/.direnv/cache"
            echo "🧰 templates workbench — 'just new <template> <dest>' to scaffold"
          '';
        };
      });
    };
}
