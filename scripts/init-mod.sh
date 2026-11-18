#!/usr/bin/env bash
# 一次性派生: scripts/init-mod.sh STS2-Foo [Foo] [--cn-name "中文名"]
# [--name "英文名"] [--summary "简介"] [--author "作者"] [--repo Owner/Repository] [--verify-build] [--commit] [--fresh-git]
# 默认只验源码;--verify-build 使用 dev-env 配置的当前游戏目标,在改名前预检依赖。
set -euo pipefail
cd "$(dirname "$0")/.."
NEW_ID="${1:?用法: init-mod.sh STS2-<PascalName> [PascalName] [--cn-name ...]}"
shift
SHORT=""; NAME=""; CN=""; SUMMARY=""; AUTHOR=""; REPO=""; VERIFY_BUILD=0; DO_COMMIT=0; FRESH_GIT=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) NAME="${2:?--name 需要值}"; shift 2 ;;
        --cn-name) CN="${2:?--cn-name 需要值}"; shift 2 ;;
        --summary) SUMMARY="${2:?--summary 需要值}"; shift 2 ;;
        --author) AUTHOR="${2:?--author 需要值}"; shift 2 ;;
        --repo) REPO="${2:?--repo 需要 Owner/Repository}"; shift 2 ;;
        --verify-build) VERIFY_BUILD=1; shift ;;
        --commit) DO_COMMIT=1; shift ;;
        --fresh-git) FRESH_GIT=1; shift ;;
        --*) echo "错误: 未知参数 $1" >&2; exit 2 ;;
        *) [[ -z "$SHORT" ]] || { echo '错误: 只能指定一个 PascalName。' >&2; exit 2; }
           SHORT="$1"; shift ;;
    esac
done
SHORT="${SHORT:-${NEW_ID#STS2-}}"
[[ "$SHORT" =~ ^[A-Z][A-Za-z0-9]*$ && "$NEW_ID" == "STS2-$SHORT" && "$SHORT" != Template ]] || {
    echo '错误: 身份必须为 STS2-<PascalName>,且不能派生成模板自身。' >&2; exit 1;
}
[[ -f STS2-Template.json ]] || { echo '错误: 缺模板清单;不能重复初始化。' >&2; exit 1; }
REPO="${REPO:-SlayTheCircle/$NEW_ID}"
[[ "$REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || { echo '错误: --repo 必须为 Owner/Repository。' >&2; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null
[[ "$(git rev-parse --show-toplevel)" == "$PWD" ]] || { echo '错误: 模板必须位于自己的 Git 仓库根目录。' >&2; exit 1; }
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    [[ -z "$(git status --porcelain)" ]] || { echo '错误: 工作树不干净;先完成或还原已有修改。' >&2; exit 1; }
else
    # 源码 ZIP 可 git init + git add 后派生,不要求先创建提交。初始索引就是输入快照。
    git diff --quiet
    [[ -z "$(git ls-files --others --exclude-standard)" && -n "$(git ls-files)" ]] || {
        echo '错误: 无历史的仓库须先 git add 初始源码快照。' >&2; exit 1;
    }
fi
if [[ "$VERIFY_BUILD" == 1 ]]; then
    source scripts/dev-env.sh
    mod_require_refs
fi
# 先验证输入快照,失效文档或本地化不得在结构改名后才被发现。
./scripts/check.sh --source-only
CN="${CN:-$SHORT}"; NAME="${NAME:-$SHORT}"; SUMMARY="${SUMMARY:-${CN}角色模组}"
AUTHOR="${AUTHOR:-$(git config user.name || true)}"; AUTHOR="${AUTHOR:-SlayTheCircle}"
export PYTHONPATH="$PWD/scripts${PYTHONPATH:+:$PYTHONPATH}"
echo "派生: STS2-Template → $NEW_ID"
python3 -m derivation "$NEW_ID" "$SHORT" "$CN" "$NAME" "$SUMMARY" "$AUTHOR" "$REPO"
# 单次脚手架退出派生仓;检查最终树,避免被检查过的文件随后删除。
git rm -q -f scripts/init-mod.sh
for directory in templates scripts/derivation tests/TemplatePipeline; do
    if [[ -n "$(git ls-files -- "$directory")" ]]; then git rm -q -r -f "$directory"; fi
done
python3 scripts/export-card-table.py
./scripts/check.sh --source-only
# 只检查运行内容的旧身份;谱系、通用文档和私有资料不属于运行时身份。
if grep -rnE --include='*.cs' --include='*.csproj' --include='*.json' --include='*.yml' 'STS2-Template\b|STS2_TEMPLATE_|\bTemplateMod\b|template_support\.png' src localization .github/workflows/release.yml; then
    echo '错误: 运行内容仍含模板身份。' >&2; exit 1
fi
if [[ "$VERIFY_BUILD" == 1 ]]; then
    ./scripts/build.sh --dll-only
else
    echo '未执行编译;配置依赖后运行 build.sh --dll-only,或初始化时指定 --verify-build。'
fi
if [[ "$FRESH_GIT" == 1 ]]; then
    rm -rf .git
    git init -b main -q
    git add -A
fi
if [[ "$DO_COMMIT" == 1 ]]; then
    git add -A
    git commit -m "chore: derive $NEW_ID from STS2-Template"
fi
echo '完成;继续阅读 docs/dev/onboarding.md 与 local_dev/README.md。'
