# 事件实现（可选模块）

骨架不含事件内容；需要时按本页接线。事件基线类 `Content/Events/<Short>EventBase.cs`。

## 注册与门控

新事件继承 `<Short>EventBase`，由 RitsuLib 的 RegisterActEvent 注册到对应 Act。IsAllowed 查询队伍中是否有本角色——「队伍含本角色」与「事件归属者是本角色」（原版追加选项查询事件 Owner.Character）是**两种不同门控**，多人验收应覆盖两者。

## 原版追加选项

给原版事件追加角色专属选项：在 `EventModel.GenerateInitialOptionsWrapper` 基方法上打 Harmony postfix（按当前版本原版方法与 Harmony API 核对）。要点：

- 当前目标未覆写该方法；游戏升级时重新核对方法及目标类。
- SetEventFinished 是受保护成员，外部处理器使用启动时缓存的反射委托；找不到方法时记录错误并停止追加，保留原版选项。
- 原版追加选项使用原版 Entry 下的 `<MOD>_*` 键。

## 初始化通道（关键教训）

**ModEntry 带 ModInitializer 时，游戏加载器不会再自动 PatchAll**——Init 完成注册后必须显式调用 `Harmony.PatchAll`。发现补丁类、编译通过或看到新事件注册，都不能证明追加选项已执行；补丁声明、DLL 编译、日志与真实选项出现提供不同层次的证据。

## 本地化与资源

新事件复合 Entry 为 `STS2_<MOD>_EVENT_<类名蛇形大写>`，在 `localization/{lang}/events.json` 维护：`Entry.title`、`Entry.pages.INITIAL.description`、`Entry.pages.INITIAL.options.<KEY>.title／description`、各结果页 description。ModEventTemplate 的 InitialOptionKey 和 PageDescription 拼接层级。动态变量随 CanonicalVars 声明，选牌提示、代价、悬停预览与效果一致。

事件肖像通常置于 `images/events/<类名>.png`；还必须覆写 `EventAssetProfile(InitialPortraitPath: "res://<ModId>/images/events/<类名>.png")` 或对应资源入口。ModEventTemplate 默认 AssetProfile.Empty，文件名本身不会自动接线。尺寸见[素材规范](assets.md)。

## 完整最小事件

[ExampleRestEvent](../../examples/events/ExampleRestEvent.cs)展示注册、门控、图片、选项和结果页：继承角色 EventBase，在 Overgrowth 挂 RegisterActEvent，AssetProfile 提供肖像，GenerateInitialOptions 返回 REST/LEAVE，动作完成后 SetEventFinished(PageDescription(...))。示例只有回复生命和离开，没有自定义补丁或反射；需要支付/选牌时在该事件模块增加实际处理。

配套文本在 [zhs](../../examples/localization/zhs/events.json)／[eng](../../examples/localization/eng/events.json)，与该类复合 Entry 对应。将类复制到自己的 Content/Events 后合并键、登记母版预检/派生和 assets/validation.json 的实际肖像断言。例如 `res://<ModId>/images/events/<类名>.png`，尺寸 `[1672, 941]`。该资源目录是约定而不是自动注册依据。

选项处理时 Owner 已由游戏赋值；队伍门控不能代替效果归属。按原版同类事件判断支付不足、无可选牌和空奖励池的可用选项；正常取消选择直接结束或返回当前页，依设计确认，不在选定前扣资源。事件发生在场外时，“加入手牌/下一场生效”等设计先明确作用域，见[状态手册](state.md)。追加原版选项继续走本页独立补丁通道，不能因新事件注册成功推断它们也已生效。

## 修改与验收

同步修改事件类、中英本地化、资源映射和对应设计差异。源码检查覆盖双语键集和显式文本资源，不验证每个事件页与选项的文案覆盖，PCK 检查覆盖代表性资源解析，真实游戏还需确认门控、选项、支付不足、不可操作卡、空池和奖励结果。DevConsole 的 `event <Entry>` 可直达目标事件——绕过自然生成门控，只能验收处理与呈现，不能证明 IsAllowed 或自然生成概率正确。未进行的多人、存档或边界场景如实记录。
