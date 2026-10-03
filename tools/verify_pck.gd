# 验证真实 PCK 的本地化可解析；不代替游戏运行时验收。
# 必需纹理由 scripts/asset_contract.py 生成;额外槽登记 assets/validation.json。
# 合法空本地化对象表示未启用模块;场景生命周期和机制仍需真实游戏验收。
extends SceneTree

const TextureVerifier = preload("verify_textures.gd")

const TABLES := ["cards", "powers", "relics", "potions", "characters", "card_keywords",
	"card_selection", "events", "enchantments", "epochs", "ancients"]

var _frame := 0
var _mod_id := ""

func _process(_delta: float) -> bool:
	_frame += 1
	if _frame != 1:
		return true
	_mod_id = OS.get_environment("MOD_ID")
	if _mod_id.is_empty():
		push_error("MOD_ID not set")
		quit(1)
		return true
	var pck := OS.get_environment("MOD_PCK")
	if pck.is_empty() or not ProjectSettings.load_resource_pack(pck, true):
		push_error("PCK 挂载失败")
		quit(1)
		return true
	var failures := 0
	for lang in ["zhs", "eng"]:
		for table in TABLES:
			failures += _verify_localization(lang, table)
	var contract_path := OS.get_environment("MOD_ASSET_CONTRACT")
	if not contract_path.is_empty():
		var contract = JSON.parse_string(FileAccess.get_file_as_string(contract_path))
		if not contract is Dictionary:
			push_error("PCK 资源断言清单不可解析")
			failures += 1
		else:
			failures += TextureVerifier.verify(contract)
	if failures == 0:
		print("PCK 本地化可解析；资源断言: " + ("已验证" if not contract_path.is_empty() else "未执行") + "；未验证游戏模型、场景生命周期或机制。")
	quit(0 if failures == 0 else 1)
	return true

func _verify_localization(lang: String, table: String) -> int:
	var path := "res://%s/localization/%s/%s.json" % [_mod_id, lang, table]
	if not FileAccess.file_exists(path):
		push_error("PCK 缺本地化: " + path)
		return 1
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not parsed is Dictionary:
		push_error("PCK 本地化不可解析: " + path)
		return 1
	return 0
