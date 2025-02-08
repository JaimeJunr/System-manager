import platform

import psutil
import time

from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt
from pynput import keyboard

# Variáveis globais para a navegação e controle
selected_tab = 0
monitoring = True  # Variável para controlar se o monitoramento está ativo
console = Console()

def get_network_info():
    """Obtém informações de uso da rede."""
    net_io = psutil.net_io_counters()
    table = Table(title="Monitoramento de Rede", box=box.SIMPLE)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")

    table.add_row("Bytes Enviados", f"{net_io.bytes_sent / (1024 ** 2):.2f} MB")
    table.add_row("Bytes Recebidos", f"{net_io.bytes_recv / (1024 ** 2):.2f} MB")
    return table


def get_temperature_info():
    """Obtém informações de temperatura da CPU e GPU, se suportado."""
    try:
        temperatures = psutil.sensors_temperatures()


        # Busque em outras seções, como 'acpi_thermal' ou 'k10temp' (para AMD)
        cpu_temp = temperatures.get('acpi_thermal', temperatures.get('k10temp', []))

        if cpu_temp:
            cpu_temp = cpu_temp[0].current  # Pegue a primeira temperatura disponível
        else:
            raise ValueError("Nenhum sensor de temperatura disponível.")

        table = Table(title="Temperatura do Sistema", box=box.SIMPLE)
        table.add_column("Componente", style="cyan", no_wrap=True)
        table.add_column("Temperatura", style="magenta")

        table.add_row("CPU", f"{cpu_temp:.1f} °C")
        return table
    except Exception as e:
        return f"Erro ao obter temperaturas: {e}"


def get_system_info():
    """Obtém informações básicas do sistema."""
    system_info = platform.uname()
    table = Table(title="Informações do Sistema", box=box.SIMPLE)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")

    table.add_row("Sistema", system_info.system)
    table.add_row("Versão", system_info.version)
    table.add_row("Arquitetura", system_info.machine)
    return table

def get_memory_info():
    """Obtém informações detalhadas de uso de memória."""
    memory = psutil.virtual_memory()
    table = Table(title="Monitoramento de Memória", box=box.SIMPLE)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")

    table.add_row("Total", f"{memory.total / (1024 ** 3):.2f} GB")
    table.add_row("Disponível", f"{memory.available / (1024 ** 3):.2f} GB")
    table.add_row("Usado", f"{memory.used / (1024 ** 3):.2f} GB")
    table.add_row("Percentual", f"{memory.percent}%")
    table.add_row("Utilizado por Buffers", f"{memory.buffers / (1024 ** 3):.2f} GB")
    return table


def get_cpu_info():
    """Obtém informações de uso da CPU."""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq()
    cpu_times = psutil.cpu_times()

    table = Table(title="Monitoramento de CPU", box=box.SIMPLE)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")

    table.add_row("Uso de CPU", f"{cpu_percent}%")
    table.add_row("Frequência", f"{cpu_freq.current:.2f} MHz")
    table.add_row("Núcleos físicos", f"{psutil.cpu_count(logical=False)}")
    table.add_row("Núcleos lógicos", f"{psutil.cpu_count(logical=True)}")
    table.add_row("Tempo de usuário", f"{cpu_times.user:.2f} s")
    table.add_row("Tempo de sistema", f"{cpu_times.system:.2f} s")
    return table


def get_disk_info():
    """Obtém informações de uso do disco."""
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()

    table = Table(title="Monitoramento de Disco", box=box.SIMPLE)
    table.add_column("Propriedade", style="cyan", no_wrap=True)
    table.add_column("Valor", style="magenta")

    table.add_row("Total", f"{disk.total / (1024 ** 3):.2f} GB")
    table.add_row("Usado", f"{disk.used / (1024 ** 3):.2f} GB")
    table.add_row("Livre", f"{disk.free / (1024 ** 3):.2f} GB")
    table.add_row("Leituras", f"{disk_io.read_bytes / (1024 ** 3):.2f} GB")  # Adicionado estatísticas de E/S
    table.add_row("Escritas", f"{disk_io.write_bytes / (1024 ** 3):.2f} GB")
    table.add_row("Percentual", f"{disk.percent}%")
    return table


def check_alerts(cpu_percent, memory_percent, disk_percent):
    """Verifica se os valores de uso ultrapassam limites e emite alertas."""
    if cpu_percent > 80:
        console.log("[red]Alerta: Uso de CPU acima de 80%![/red]")
    if memory_percent > 80:
        console.log("[red]Alerta: Uso de Memória acima de 80%![/red]")
    if disk_percent > 80:
        console.log("[red]Alerta: Uso de Disco acima de 80%![/red]")


def draw_interface():
    """Desenha a interface com abas e informações do sistema."""
    layout = Layout()

    # Menu de navegação com destaque na aba selecionada
    menu_text = Text("[{}] Sistema  [{}] Memória  [{}] CPU  [{}] Disco  [{}] Rede  [{}] Temperatura".format(
        '*' if selected_tab == 0 else ' ',
        '*' if selected_tab == 1 else ' ',
        '*' if selected_tab == 2 else ' ',
        '*' if selected_tab == 3 else ' ',
        '*' if selected_tab == 4 else ' ',
        '*' if selected_tab == 5 else ' '
    ))
    layout.split_column(
        Layout(Panel(menu_text, title="Menu")),
        Layout(name="content")
    )


    # Renderiza o painel de acordo com a aba selecionada
    if selected_tab == 0:
        layout["content"].update(Panel(get_system_info(), title="Sistema"))
    elif selected_tab == 1:
        layout["content"].update(Panel(get_memory_info(), title="Memória"))
    elif selected_tab == 2:
        layout["content"].update(Panel(get_cpu_info(), title="CPU"))
    elif selected_tab == 3:
        layout["content"].update(Panel(get_disk_info(), title="Disco"))
    elif selected_tab == 4:
        layout["content"].update(Panel(get_network_info(), title="Rede"))
    elif selected_tab == 5:
        layout["content"].update(Panel(get_temperature_info(), title="Temperatura"))

    return layout


def display_help():
    """Exibe a ajuda com os comandos disponíveis."""
    help_text = Text("Comandos disponíveis:\n"
                     "- Direita: Navegar para a próxima aba\n"
                     "- Esquerda: Navegar para a aba anterior\n"
                     "- Espaço: Ativar/desativar monitoramento\n"
                     "- Esc: Sair do monitoramento", style="green")
    console.print(help_text)


def on_press(key):
    """Lida com os eventos de teclas para navegação e controle do monitoramento."""
    global selected_tab, monitoring
    try:
        if key == keyboard.Key.right:
            selected_tab = (selected_tab + 1) % 6  # Atualizado para 6 abas
        elif key == keyboard.Key.left:
            selected_tab = (selected_tab - 1) % 6  # Atualizado para 6 abas
        elif key == keyboard.Key.esc:
            console.log("Saindo do monitoramento...")
            return False
        elif key == keyboard.Key.space:
            monitoring = not monitoring
            status = "ativado" if monitoring else "desativado"
            console.log(f"Monitoramento {status}.")
    except Exception as e:
        console.print(f"[red]Erro:[/red] {e}")

def monitor():
    """Monitora o sistema e atualiza as informações."""
    global monitoring
    with Live(draw_interface(), refresh_per_second=2, console=console, screen=True, transient=True) as live:
        while True:
            if monitoring:
                # Obtém dados do sistema
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent

                # Verifica e emite alertas
                check_alerts(cpu_percent, memory_percent, disk_percent)

            live.update(draw_interface())
            time.sleep(0.5)  # Atualiza as informações com um pequeno atraso



def main():
    # Adiciona escutador de teclado
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Inicia o monitoramento
    monitor()


if __name__ == "__main__":
    main()
