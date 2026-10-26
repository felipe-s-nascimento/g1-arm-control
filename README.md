# Unitree G1 – DualSense Low-Level Controller

## Português

Controle de baixo nível para o robô humanóide **Unitree G1** usando um controle
**DualSense** (PS5). Permite mover braços (ombro, cotovelo, punho), gravar poses
e reproduzi-las em sequência ou em loop.

> ⚠️ **Aviso de segurança**: mantenha o robô **suspenso** ou em uma área segura.
> O modo **Sport Mode** deve estar **desativado**. O controle de baixo nível só
> funciona após entrar no **modo de desenvolvedor** com o controle da Unitree
> (L2 + R2).

> 💡 **Não tem o robô G1?** Você pode testar todo o controlador no simulador
> oficial **[Unitree MuJoCo](#simulação-no-unitree-mujoco)** (somente Linux).
> Nesse caso, o robô físico **não é necessário** — apenas o simulador, o
> DualSense e o SDK da Unitree.

## Funcionalidades

- Controle incremental dos braços esquerdo e direito em tempo real.
- Troca de braço com o botão **Touchpad**.
- Gravação de poses com **L3**.
- Reprodução única (**R3**) ou em loop (**Options**).
- Limpeza de todas as poses com **Share**.
- Inicialização suave com rampa de ganhos (damping → interpolação).


## 🎥 Vídeo de Demonstração / Demo Video

[![Assista ao vídeo de demonstração]](https://github.com/user-attachments/assets/e191cfc5-67a1-434d-8e96-d9a9fcaaccd4)

## Requisitos

### Hardware
- Robô Unitree G1 **ou** o simulador Unitree MuJoCo (veja a seção de simulação abaixo).
- Controle DualSense (conectado via USB ou Bluetooth).
- Computador com interface de rede conectada ao robô (ex.: `enp2s0`, `en1`, `eth0`).
  Se estiver usando apenas o simulador, a interface `lo` (loopback) é suficiente.

### Software
- Python 3.8+.
- [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python).
- `cyclonedds==0.10.2`, `numpy`, `opencv-python` (dependências do SDK).
- `pygame` (para o DualSense).
- No Linux: usuário no grupo `input` para acessar o joystick.

## Instalação

1. Instale o SDK da Unitree (veja o [README oficial](https://github.com/unitreerobotics/unitree_sdk2_python) para detalhes):
   ```bash
   git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
   cd unitree_sdk2_python
   pip3 install -e .
   ```
   Se der erro de `cyclonedds`, compile-o primeiro e defina `CYCLONEDDS_HOME`.

2. Instale as dependências Python restantes:
   ```bash
   pip3 install pygame numpy
   ```

3. Clone este repositório:
   ```bash
   git clone https://github.com/felipe-s-nascimento/g1-arm-control.git
   cd g1-arm-control
   ```

## Simulação no Unitree MuJoCo

**Não tem o robô físico? Sem problema.** Você pode testar todo o controlador
no simulador oficial da Unitree, que utiliza o mesmo SDK2 e as mesmas mensagens
DDS (`LowCmd` / `LowState`) do robô real. Para o controlador, é **indiferente**
se os comandos estão indo para o G1 físico ou para o simulador — o código,
o mapeamento do DualSense e a lógica de gravação/reprodução funcionam
exatamente da mesma forma.

> 🐧 **Requisito de sistema operacional**: o simulador Unitree MuJoCo roda
> **somente em Linux** (Ubuntu 20.04 / 22.04 recomendado). Não há suporte
> oficial para **macOS** ou **Windows**. Se você estiver no macOS, utilize uma
> máquina virtual Linux, um container Docker com suporte a GUI, ou uma máquina
> Linux dedicada para rodar a simulação.

### Repositório oficial

- **Unitree MuJoCo**: [https://github.com/unitreerobotics/unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco)

### Configuração

1. Clone o simulador:
   ```bash
   git clone https://github.com/unitreerobotics/unitree_mujoco.git
   cd unitree_mujoco
   ```

2. Instale as dependências do simulador (Python):
   ```bash
   pip3 install mujoco
   ```

3. Edite o arquivo `simulate_python/config.py` e ajuste as duas primeiras variáveis para o G1:
   ```python
   ROBOT = "g1"  # Robot name: "go2", "b2", "b2w", "h1", "go2w", "g1"
   ROBOT_SCENE = "../unitree_robots/" + ROBOT + "/scene_23dof.xml"
   ```
   > Para o G1 de **29 DOF** (com punhos e cintura), use `scene_29dof.xml` se disponível.

4. Execute o simulador:
   ```bash
   python3 simulate_python/unitree_mujoco.py
   ```

5. Em outro terminal, execute o controlador deste projeto apontando para a interface de loopback:
   ```bash
   python3 run_controller.py lo
   ```
   O controlador irá se conectar ao simulador via DDS na mesma máquina, permitindo
   testar o mapeamento do DualSense e a lógica de gravação/reprodução sem o robô real.

### Notas

- O simulador suporta apenas **desenvolvimento de baixo nível** (`LowCmd` / `LowState`), exatamente o que este projeto utiliza.
- **Não é necessário entrar em modo de desenvolvedor** no simulador — o próprio
  simulador já inicia no modo correto para receber comandos de baixo nível.
- Certifique-se de que o **domain ID** do DDS esteja igual ao usado pelo simulador (padrão: `0`).
- Para evitar conflitos com o robô real, use a interface `lo` (loopback) durante a simulação.
- O simulador só funciona em **Linux**. Em macOS, uma alternativa leve é usar
  apenas o **controlador** com `mapping.py` para validar o mapeamento dos botões
  do DualSense, sem simulação.

## Uso

### Com o robô físico
1. Conecte o DualSense ao computador.
2. Coloque o robô no **modo de desenvolvedor** usando o **controle da Unitree**
   (pressione **L2 + R2** no controle da Unitree).
3. Execute o controlador passando a interface de rede:
   ```bash
   python3 run_controller.py <interface>
   ```
   Exemplo:
   ```bash
   python3 run_controller.py enp2s0
   ```
4. Pressione **Options** no DualSense para iniciar o controle.

### Com o simulador (sem robô físico)
1. Inicie o simulador Unitree MuJoCo (veja a seção acima).
2. Conecte o DualSense ao computador.
3. Execute o controlador apontando para a interface de loopback:
   ```bash
   python3 run_controller.py lo
   ```
4. Pressione **Options** no DualSense para iniciar o controle.

## Mapeamento do DualSense

| Entrada | Ação |
|---|---|
| **Stick esquerdo** | Yaw e cotovelo do braço ativo |
| **Stick direito** | Roll e pitch do ombro |
| **L2 / R2** | Rotação do punho (wrist roll) |
| **L1 / R1 (botões 9 / 10)** | Rotação do punho (wrist yaw) (+) / (−) |
| **D-pad ← / → (botões 13 / 14)** | Inclinação do punho (wrist pitch) (+) / (−) |
| **Touchpad (botão 15)** | Alterna entre braço direito e esquerdo |
| **L3 (botão 7)** | Grava pose atual |
| **R3 (botão 8)** | Reproduz poses uma vez |
| **Options (botão 6)** | Inicia/para reprodução em loop |
| **Share (botão 4)** | Apaga todas as poses gravadas |
| **Ctrl+C** | Encerra o programa |

> ℹ️ Os números dos botões podem variar entre sistemas operacionais (macOS,
> Linux, Windows). Rode `python3 mapping.py` para confirmar a numeração exata
> no seu sistema.

## Estrutura do projeto

```
.
├── config/
│   └── settings.py          # Parâmetros, limites, ganhos, modos, pose inicial
├── controller/
│   └── g1_controller.py     # Lógica de controle, gravação e reprodução
├── mapping.py               # Script para descobrir números dos botões do controle
├── run_controller.py        # Entrypoint principal
└── README.md
```

## Segurança

- Nunca execute sem o robô estar suspenso ou em área segura.
- O modo de baixo nível **ignora** os controladores internos do G1; certifique-se
  de que o **Sport Mode** está desativado.
- Ajuste os ganhos em `JOINT_GAINS` (em `config/settings.py`) se ouvir zumbido
  ou vibração excessiva.
- Se estiver usando apenas o simulador, essas precauções **não se aplicam** —
  o MuJoCo é um ambiente virtual e não oferece risco físico.

## Referências

- [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python)
- [Unitree MuJoCo](https://github.com/unitreerobotics/unitree_mujoco)
- [Documentação do Unitree G1](https://support.unitree.com/home/en/developer/Quick_start)
- [PyPI – pygame](https://pypi.org/project/pygame/)

---

## English

Low-level control for the **Unitree G1** humanoid robot using a **DualSense**
(PS5) controller. Allows moving arms (shoulder, elbow, wrist), recording poses,
and playing them back in sequence or in a loop.

> ⚠️ **Safety warning**: keep the robot **suspended** or in a safe area.
> **Sport Mode** must be **disabled**. Low-level control only works after
> entering **developer mode** with the Unitree controller (L2 + R2).

> 💡 **Don't have the G1 robot?** You can test the whole controller in the
> official **[Unitree MuJoCo](#unitree-mujoco-simulation)** simulator
> (Linux only). In that case, the physical robot is **not required** — only
> the simulator, the DualSense, and the Unitree SDK.

## Features

- Real-time incremental control of left and right arms.
- Switch arms with the **Touchpad** button.
- Record poses with **L3**.
- Playback once (**R3**) or in a loop (**Options**).
- Clear all recorded poses with **Share**.
- Smooth initialisation with gain ramp (damping → interpolation).

## Requirements

### Hardware
- Unitree G1 robot **or** the Unitree MuJoCo simulator (see the simulation section below).
- DualSense controller (connected via USB or Bluetooth).
- Computer with a network interface connected to the robot (e.g. `enp2s0`, `en1`, `eth0`).
  If you are using only the simulator, the `lo` (loopback) interface is enough.

### Software
- Python 3.8+.
- [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python).
- `cyclonedds==0.10.2`, `numpy`, `opencv-python` (SDK dependencies).
- `pygame` (for the DualSense).
- On Linux: user in the `input` group to access the joystick.

## Installation

1. Install the Unitree SDK (see the [official README](https://github.com/unitreerobotics/unitree_sdk2_python) for details):
   ```bash
   git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
   cd unitree_sdk2_python
   pip3 install -e .
   ```
   If you get a `cyclonedds` error, compile it first and set `CYCLONEDDS_HOME`.

2. Install the remaining Python dependencies:
   ```bash
   pip3 install pygame numpy
   ```

3. Clone this repository:
   ```bash
   git clone https://github.com/felipe-s-nascimento/g1-arm-control.git
   cd g1-arm-control
   ```

## Unitree MuJoCo Simulation

**No physical robot? No problem.** You can test the whole controller in the
official Unitree simulator, which uses the same SDK2 and DDS messages
(`LowCmd` / `LowState`) as the real robot. For the controller, it is
**indifferent** whether the commands are going to the physical G1 or to the
simulator — the code, the DualSense mapping, and the recording/playback logic
work exactly the same way.

> 🐧 **Operating system requirement**: the Unitree MuJoCo simulator runs
> **only on Linux** (Ubuntu 20.04 / 22.04 recommended). There is no official
> support for **macOS** or **Windows**. If you are on macOS, use a Linux
> virtual machine, a Docker container with GUI support, or a dedicated Linux
> machine to run the simulation.

### Official repository

- **Unitree MuJoCo**: [https://github.com/unitreerobotics/unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco)

### Setup

1. Clone the simulator:
   ```bash
   git clone https://github.com/unitreerobotics/unitree_mujoco.git
   cd unitree_mujoco
   ```

2. Install the simulator dependencies (Python):
   ```bash
   pip3 install mujoco
   ```

3. Edit `simulate_python/config.py` and adjust the first two variables for the G1:
   ```python
   ROBOT = "g1"  # Robot name: "go2", "b2", "b2w", "h1", "go2w", "g1"
   ROBOT_SCENE = "../unitree_robots/" + ROBOT + "/scene_23dof.xml"
   ```
   > For the **29-DOF** G1 (with wrists and waist), use `scene_29dof.xml` if available.

4. Run the simulator:
   ```bash
   python3 simulate_python/unitree_mujoco.py
   ```

5. In another terminal, run this project's controller pointing to the loopback interface:
   ```bash
   python3 run_controller.py lo
   ```
   The controller will connect to the simulator via DDS on the same machine,
   allowing you to test the DualSense mapping and the recording/playback logic
   without the real robot.

### Notes

- The simulator only supports **low-level development** (`LowCmd` / `LowState`),
  which is exactly what this project uses.
- **No need to enter developer mode** in the simulator — the simulator itself
  already starts in the correct mode to receive low-level commands.
- Make sure the DDS **domain ID** matches the one used by the simulator (default: `0`).
- To avoid conflicts with the real robot, use the `lo` (loopback) interface during simulation.
- The simulator runs **only on Linux**. On macOS, a lightweight alternative is
  to use only the **controller** with `mapping.py` to validate the DualSense
  button mapping, without simulation.

## Usage

### With the physical robot
1. Connect the DualSense to the computer.
2. Put the robot into **developer mode** using the **Unitree controller**
   (press **L2 + R2** on the Unitree controller).
3. Run the controller passing the network interface:
   ```bash
   python3 run_controller.py <interface>
   ```
   Example:
   ```bash
   python3 run_controller.py enp2s0
   ```
4. Press **Options** on the DualSense to start control.

### With the simulator (no physical robot)
1. Start the Unitree MuJoCo simulator (see the section above).
2. Connect the DualSense to the computer.
3. Run the controller pointing to the loopback interface:
   ```bash
   python3 run_controller.py lo
   ```
4. Press **Options** on the DualSense to start control.

## DualSense Mapping

| Input | Action |
|---|---|
| **Left stick** | Yaw and elbow of the active arm |
| **Right stick** | Shoulder roll and pitch |
| **L2 / R2** | Wrist roll rotation |
| **L1 / R1 (buttons 9 / 10)** | Wrist yaw rotation (+) / (−) |
| **D-pad ← / → (buttons 13 / 14)** | Wrist pitch rotation (+) / (−) |
| **Touchpad (button 15)** | Toggle between right and left arm |
| **L3 (button 7)** | Record current pose |
| **R3 (button 8)** | Play poses once |
| **Options (button 6)** | Start/stop loop playback |
| **Share (button 4)** | Clear all recorded poses |
| **Ctrl+C** | Exit the program |

> ℹ️ Button numbers may vary between operating systems (macOS, Linux,
> Windows). Run `python3 mapping.py` to confirm the exact numbering on your
> system.

## Project structure

```
.
├── config/
│   └── settings.py          # Parameters, limits, gains, modes, initial pose
├── controller/
│   └── g1_controller.py     # Control logic, recording and playback
├── mapping.py               # Script to discover controller button numbers
├── run_controller.py        # Main entrypoint
└── README.md
```

## Safety

- Never run without the robot suspended or in a safe area.
- Low-level mode **bypasses** the G1's internal controllers; make sure
  **Sport Mode** is disabled.
- Adjust gains in `JOINT_GAINS` (in `config/settings.py`) if you hear buzzing
  or excessive vibration.
- If you are using only the simulator, these precautions **do not apply** —
  MuJoCo is a virtual environment and poses no physical risk.

## References

- [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python)
- [Unitree MuJoCo](https://github.com/unitreerobotics/unitree_mujoco)
- [Unitree G1 Documentation](https://support.unitree.com/home/en/developer/Quick_start)
- [PyPI – pygame](https://pypi.org/project/pygame/)
