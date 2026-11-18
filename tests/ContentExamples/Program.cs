using System.Reflection;
using System.Runtime.Loader;

// 把运行依赖解析与游戏类型调用分开，避免 JIT 在安装解析器前加载游戏 DLL。
AssemblyLoadContext.Default.Resolving += (_, name) =>
{
    string? path = args.Select(dir => Path.Combine(dir, name.Name + ".dll")).FirstOrDefault(File.Exists);
    return path is null ? null : AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.GetFullPath(path));
};
return ContractProbe.Run();
