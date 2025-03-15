import cv2 as cv
import RPi.GPIO as GPIO
import time

# Configuração dos servos
GPIO.setmode(GPIO.BCM)
SERVO_X_PIN = 17  # Pino para movimento horizontal
SERVO_Y_PIN = 27  # Pino para movimento vertical
GPIO.setup(SERVO_X_PIN, GPIO.OUT)
GPIO.setup(SERVO_Y_PIN, GPIO.OUT)

# PWM para os servos
servo_x = GPIO.PWM(SERVO_X_PIN, 50)  # 50 Hz
servo_y = GPIO.PWM(SERVO_Y_PIN, 50)
servo_x.start(7.5)  # Posição neutra
servo_y.start(7.5)

def set_servo_angle(servo, angle):
    duty = (angle / 18) + 2.5
    servo.ChangeDutyCycle(duty)
    time.sleep(0.2)

# Mapeamento de posições para ângulos
position_to_angle = {
    "top_left": (45, 45), "top_center": (90, 45), "top_right": (135, 45),
    "middle_left": (45, 90), "middle_center": (90, 90), "middle_right": (135, 90),
    "bottom_left": (45, 135), "bottom_center": (90, 135), "bottom_right": (135, 135)
}

# Classe de ações que movimentam os servos
class Action:
    def __init__(self):
        self.actions = {
            "look_at_top_left": (135, 135), "look_at_top_center": (90, 135), "look_at_top_right": (45, 135),
            "look_at_middle_left": (135, 90), "look_at_middle_center": (90, 90), "look_at_middle_right": (45, 90),
            "look_at_bottom_left": (135, 45), "look_at_bottom_center": (90, 45), "look_at_bottom_right": (45, 45)
        }
    
    def execute(self, action_name):
        if action_name in self.actions:
            angle_x, angle_y = self.actions[action_name]
            set_servo_angle(servo_x, angle_x)
            set_servo_angle(servo_y, angle_y)

# Classe de planejamento
class PlanLibrary:
    def __init__(self):
        self.plans = {}
    
    def set_plan_library(self, planlb):
        self.plans = planlb
    
    def get_plan(self, goal, bb):
        for g, plan_entry in self.plans:
            if g == goal and set(plan_entry['context'].items()).issubset(bb.items()):
                return plan_entry['plan']
        return None

# Classe do agente
class Agent:
    def __init__(self):
        self.beliefs = {}
        self.desires = []
        self.intention = []
        self.plan_library = PlanLibrary()
    
    def add_beliefs(self, beliefs):
        self.beliefs.update(beliefs)
    
    def add_desires(self, desire):
        self.desires.append(desire)
    
    def get_desires(self):
        return self.desires.pop()
    
    def set_plan_library(self, pl):
        self.plan_library.set_plan_library(pl)
    
    def update_intention(self, goal):
        plan = self.plan_library.get_plan(goal, self.beliefs)
        if plan:
            self.intention.extend(plan)
    
    def execute_intention(self):
        action_instance = Action()
        while self.intention:
            next_action = self.intention.pop()
            action_instance.execute(next_action)

# Inicialização do agente
agent = Agent()
agent.add_beliefs({'profile': "shy", 'position': 'middle_center'})
agent.add_desires("adjust_vision")
agent.set_plan_library([
    ('adjust_vision', {'context': {'position': 'top_left', 'profile': 'shy'}, 'plan': ['look_at_top_left']}),
    ('adjust_vision', {'context': {'position': 'top_center', 'profile': 'shy'}, 'plan': ['look_at_top_center']}),
    ('adjust_vision', {'context': {'position': 'top_right', 'profile': 'shy'}, 'plan': ['look_at_top_right']}),
    ('adjust_vision', {'context': {'position': 'middle_left', 'profile': 'shy'}, 'plan': ['look_at_middle_left']}),
    ('adjust_vision', {'context': {'position': 'middle_center', 'profile': 'shy'}, 'plan': ['look_at_middle_center']}),
    ('adjust_vision', {'context': {'position': 'middle_right', 'profile': 'shy'}, 'plan': ['look_at_middle_right']}),
    ('adjust_vision', {'context': {'position': 'bottom_left', 'profile': 'shy'}, 'plan': ['look_at_bottom_left']}),
    ('adjust_vision', {'context': {'position': 'bottom_center', 'profile': 'shy'}, 'plan': ['look_at_bottom_center']}),
    ('adjust_vision', {'context': {'position': 'bottom_right', 'profile': 'shy'}, 'plan': ['look_at_bottom_right']}),
])

# Loop contínuo para executar o agente
try:
    while True:
        goal = agent.get_desires()
        agent.update_intention(goal)
        agent.execute_intention()
        time.sleep(1)  # Pequena pausa para evitar loop muito rápido
except KeyboardInterrupt:
    print("Encerrando execução...")
    servo_x.stop()
    servo_y.stop()
    GPIO.cleanup()
