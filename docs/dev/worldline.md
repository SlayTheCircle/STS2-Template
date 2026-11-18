# 世界线（可选模块）

世界线＝角色 Mod 的章节揭示／内容解锁／先古对话体系。**模板骨架不含角色专属故事代码**，衍生仓按自己的章节、奖励与解锁设计实现。本页维护基类、注册、资源和验收契约；具体 API 签名按同版本 RitsuLib 文档核对，行为先例查对应游戏版本的原版实现。

## 章节与三池门控

故事与纪元**必须继承 RitsuLib 脚手架基类**：ModStoryTemplate（Id 由 StoryKey 推导，章节顺序来自 RegisterStoryEpoch 的绑定）。内容解锁章继承 Relic／Potion／CardUnlockEpochTemplate；它们的原版展示格式读取前三件，RitsuLib 0.6.2 要求至少三件，通常按设计三件一章，超过三件时须核对实际展示。角色解锁章继承 `CharacterUnlockEpochTemplate<TCharacter>`，不受三件内容奖励要求约束。原版时间线屏幕的槽位合并按 `is ModEpochTemplate` 过滤，直接继承 EpochModel 会出现「解锁链照常触发但整列不渲染」——该契约不可绕过。

奖励 UI 与内容可获得性分别接线：模板 QueueUnlocks 负责揭示界面；`ModUnlockRegistry.RequireEpoch` 登记模型的纪元条件，与纪元类的 CardTypes／RelicTypes／PotionTypes 共用同一来源，不另抄一份列表。RitsuLib 维护相应解锁过滤；自定义奖励路径仍须查询该局的 UnlockState，不能用 AllCards 等全量列表绕过。变更章节奖励时同时更新数组、门控、两语言文本及验收场景。

## 最小两章接线

完整代码见 [ExampleTimeline](../../examples/timeline/ExampleTimeline.cs)、[故事](../../examples/timeline/ExampleStory.cs)、[角色解锁章](../../examples/timeline/ExampleCharacterEpoch.cs)、[三卡章](../../examples/timeline/ExampleCardsEpoch.cs)。例子采用显式注册，使顺序可读：

1. ModEntry 先登记程序集归属，再调用 ExampleTimeline.Register 一次。该模块按顺序 RegisterStoryEpoch；不再给相同类型添加等效注册属性。
2. 第一章以 CharacterUnlockEpochTemplate 解锁角色，并声明 ExpansionEpochTypes 揭示第二章。布局先申请 FarFuture0 之前的空列，再把第二章放同一列；不用固定数字猜槽位。
3. RequireEpoch 把角色绑定第一章，UnlockCharacterAfterRunAs 把自然条件绑定“以铁甲战士结束一局”。第一章不能要求尚未解锁的角色自己完成一局。
4. 第二章复用 EnumerateUnlockCardTypes 登记三张奖励卡的条件，UnlockEpochAfterWinAs 绑定角色获胜。三卡类型是已注册的具体模型，不以本地化名识别。
5. 自己的第三/四章依照 RelicUnlockEpochTemplate 的 `RelicTypes` 与 PotionUnlockEpochTemplate 的 `PotionTypes` 扩展。各章的自然条件独立裁定，不从章序自动推导“下一局就解锁”。

故事 Id 是 StoryKey 经原版 Slugify 得到的键，示例为 `STS2_TEMPLATE_EXAMPLE`；epoch 的 Id 是显式稳定键，衍生时随模板身份改写，之后不要随标题变更。两语言 epochs 表维护 `STORY_<StoryId>`、`EpochId.title/description/unlockInfo`；角色解锁章还供 `unlockText`，三池解锁章用模板生成 UnlockText。文本示例在 [zhs](../../examples/localization/zhs/epochs.json)／[eng](../../examples/localization/eng/epochs.json)。本例编译不意味着自然进度与三池门控已经游戏内通过。

## 纪元肖像（全局资源）

纪元肖像是**两个独立资源槽**：大图按全局 `res://images/timeline/epoch_portraits/<键>.png` 推导（放 `assets/global/`，打包器保留全局路径，不能套用普通 Mod 前缀）；缩略图原版走 epoch_atlas 图集、mod 无图集条目会显示 NOPE，须经各纪元类的 AssetProfile.PackedPortraitPath 覆盖指向 `res://<ModId>/images/timeline/` 下的派生图（从大图裁切 272×174）。

示例通过 EpochAssetProfile 同时显式指定 PackedPortraitPath 和 BigPortraitPath；全局大图文件名含 Mod 身份，避免共享命名冲突。将实际大图/缩略图路径与尺寸登记到 assets/validation.json，才会成为自动包内断言。放图、声明路径、资源检查、真实时间线显示是四个不同证据。

## 先古对话与资源

RitsuLib 根据 `localization/{lang}/ancients.json` 自动组装对话。键族为 `<先古Entry>.talk.<角色Entry>.<序号>-<行号>.char／ancient`，续接键 `.next`。要点：

- **`.next` 是逐行键**：每轮除末行外各行都要有，缺失时游戏把键名原文回显在界面角落。
- **行号带 `r` 后缀** = 加入可重复池：轮次精确匹配用尽后从已解锁轮次随机重放（原版行为）。同轮全行（含 .next）一致，混合会抛异常。
- **同轮变体**：多段对话共享同一 VisitIndex 时，游戏在候选中随机挑一段播放；序号 >0 的变体段需 `<序号>-visit` 控制键回指轮次（如 `1-visit`=0），否则被默认映射成后续轮次。
- **拜访语义**：各先古按「角色×先古」计次；**整个存档的首次遇见由全角色共享的 firstVisitEver 通用台词占用**——纯新档各族第 0 轮不可达，与原版一致；第 N 次遇见显示 VisitIndex=N-1 的轮次。非建筑师的序号→轮次默认映射为 0→0、1→1、2→4、+3。
- 建筑师终局走同一机制：对话序号即登顶轮次，另有可选的 -visit／-attack／-startattack／-endattack 键控制编排；无键时 RitsuLib 空对话兜底并告警。
- 角色初始遗物的先古升级（欧罗巴斯之触类）：用 RitsuLib 的注册映射挂获取时替换，**不要**按「以前遇见过」的相遇记录自建持久化。

调试：控制台 `ancient <Entry>` 直达画面，但绕过自然门控，仍需自然进度验证。

## 验收边界

分别确认新档与已有档的角色可用性、揭示条件、奖励 UI、三池过滤、纪元图、先古对话。按[验证纪律](testing.md)记录各项证据。

角色未解锁、刚获得第一章、刚获胜取得三卡章，以及已有档已解锁各阶段都要观察自然路径。不能只看解锁提示；进入时间线本身，确认两图、故事列、标题与三池奖励。注册 ERROR 即使没有 Exception/NOPE，也需要逐条处理；triage-log.sh 的退出码不是验收结果。
