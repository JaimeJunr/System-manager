from pynput import keyboard
from unittest.mock import patch, MagicMock
from main import (
    get_memory_info,
    get_cpu_info,
    get_network_info,
    get_temperature_info,
    display_help,
    on_press,
    selected_tab,
    monitoring,
    console
)

# Teste para a função get_memory_info
@patch('psutil.virtual_memory')
def test_get_memory_info(mock_virtual_memory):
    mock_virtual_memory.return_value = MagicMock(
        total=16 * 1024 ** 3,
        available=8 * 1024 ** 3,
        used=7 * 1024 ** 3,
        percent=50,
        buffers=1 * 1024 ** 3
    )

    table = get_memory_info()
    assert "Total" in table.columns[0].cells
    assert "16.00 GB" in table.columns[1].cells

# Teste para a função get_cpu_info
@patch('psutil.cpu_percent')
@patch('psutil.cpu_freq')
@patch('psutil.cpu_times')
def test_get_cpu_info(mock_cpu_percent, mock_cpu_freq, mock_cpu_times):
    mock_cpu_percent.return_value = 30
    mock_cpu_freq.return_value = MagicMock(current=3000)
    mock_cpu_times.return_value = MagicMock(user=user, system=30)

    table = get_cpu_info()
    assert "Uso de CPU" in table.columns[0].cells
    assert "30%" in table.columns[1].cells

# Teste para a função get_temperature_info
@patch('psutil.sensors_temperatures')
def test_get_temperature_info(mock_sensors_temperatures):
    mock_sensors_temperatures.return_value = {'acpi_thermal': [MagicMock(current=45.0)]}

    table = get_temperature_info()
    assert "CPU" in table.rows[0]  # Verifique se a linha "CPU" está presente
    assert "45.0 °C" in table.rows[0]  # Verifique se a temperatura correta está presente

# Teste para a função display_help
def test_display_help(monkeypatch):
    console.print = MagicMock()  # Mock a função print do console
    display_help()
    console.print.assert_called_once()  # Verifica se a função print foi chamada

# Testes para a função on_press
def test_on_press_right():
    global selected_tab
    selected_tab = 0
    on_press(keyboard.Key.right)
    assert selected_tab == 1  # Verifica se a aba selecionada foi alterada

def test_on_press_left():
    global selected_tab
    selected_tab = 1
    on_press(keyboard.Key.left)
    assert selected_tab == 0  # Verifica se a aba selecionada foi alterada

def test_on_press_escape(monkeypatch):
    global monitoring
    monitoring = True
    assert on_press(keyboard.Key.esc) is False  # Verifica se retorna False para sair

def test_on_press_space(monkeypatch):
    global monitoring
    monitoring = True
    on_press(keyboard.Key.space)
    assert monitoring is False  # Verifica se o monitoramento foi desativado

