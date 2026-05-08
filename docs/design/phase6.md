Phase 6: 认知内核的终端外壳 (The CLI Shell)
我们将提供三个最核心的系统调用指令：

1. mem0 init：格式化当前目录，建立“认知基座 (Substrate)”。
2. mem0 task <id>：声明一个新的认知单元 (Manifest)。
3. mem0 run：唤醒大模型，启动认知时钟 (Cognitive Loop)。

`src/mem0ress/cli.py`

```python
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from mem0ress.core.schema import TaskManifest, CognitiveTriad, TaskStatus
from mem0ress.storage.parser import SubstrateParser
from mem0ress.core.loop import CognitiveLoop

app = typer.Typer(help="mem0ress: 认知态势感知系统内核 (Cognitive OS Kernel)")
console = Console()

SUBSTRATE_ROOT = Path(".mem0ress")

@app.command()
def init():
    """格式化当前目录，初始化认知基座 (Cognitive Substrate)"""
    tasks_dir = SUBSTRATE_ROOT / "tasks"
    if tasks_dir.exists():
        console.print("[bold yellow]⚠️ 认知基座已存在，无需重复格式化。[/bold yellow]")
        return
    
    # 构建物理目录拓扑
    tasks_dir.mkdir(parents=True, exist_ok=True)
    (SUBSTRATE_ROOT / "inbox.md").write_text("# 游离想法缓冲池\n\n", encoding="utf-8")
    
    # TODO: 这里可以挂载 git_ops.init()
    
    console.print(Panel(
        f"[bold green]✅ 认知基座 (Substrate) 格式化完成！[/bold green]\n"
        f"目录拓扑已就绪: {SUBSTRATE_ROOT.absolute()}",
        title="mem0ress Kernel"
    ))

@app.command()
def new_task(task_id: str = typer.Argument(..., help="任务ID，如 'auth_module'")):
    """在当前基座中声明一个新的意图锚点 (Task)"""
    task_dir = SUBSTRATE_ROOT / "tasks" / task_id
    if task_dir.exists():
        console.print(f"[bold red]❌ 冲突：Task '{task_id}' 已存在！[/bold red]")
        raise typer.Exit(1)
        
    task_dir.mkdir(parents=True)
    (task_dir / "gotchas").mkdir() # 创建专属经验收纳盒
    
    # 引导用户确立图景
    console.print(f"[bold cyan]正在为 Task '{task_id}' 建立意图边界...[/bold cyan]")
    picture = Prompt.ask("🎯 请用一句话描述该任务完成后的 [bold]最终图景 (Picture)[/bold]")
    
    # 实例化内存模型
    manifest = TaskManifest(
        id=task_id,
        status=TaskStatus.CREATED,
        cognitive_triad=CognitiveTriad(
            picture=picture,
            requirements=["[TODO] 请补充客观校验指标..."],
            constraints=["[TODO] 请补充执行底线..."]
        ),
        todos=[{"text": "梳理具体执行步骤", "done": False}]
    )
    
    # 物理固化
    index_path = task_dir / "index.md"
    index_path.write_text(SubstrateParser.serialize_manifest(manifest), encoding="utf-8")
    
    console.print(f"[bold green]✨ Manifest 已生成: {index_path}[/bold green]")

@app.command()
def run(max_ticks: int = typer.Option(5, help="认知时钟的最大滴答数，防止死循环")):
    """唤醒 Agent，启动认知循环 (Cognitive Loop)"""
    if not SUBSTRATE_ROOT.exists():
        console.print("[bold red]❌ 致命错误：找不到认知基座，请先运行 `mem0 init`[/bold red]")
        raise typer.Exit(1)

    console.print(Panel("[bold magenta]🧠 认知内核 (Cognitive Kernel) 启动...[/bold magenta]", border_style="magenta"))
    
    loop = CognitiveLoop(substrate_root=SUBSTRATE_ROOT)
    
    # 开始事件循环
    tick_count = 0
    try:
        while tick_count < max_ticks:
            tick_count += 1
            console.print(f"\n[bold blue]⏳ Cognitive Tick {tick_count}/{max_ticks} ...[/bold blue]")
            
            # 执行一次循环滴答 (我们在 Phase 4 中写好的核心逻辑)
            loop.tick()
            
    except KeyboardInterrupt:
        console.print("\n[bold yellow]🛑 收到中断信号，认知内核安全挂起。[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]💥 内核崩溃: {str(e)}[/bold red]")

if __name__ == "__main__":
    app()

```
