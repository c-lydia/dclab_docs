"""Session 04: original motor-drive references and the established DCLab style."""
from pathlib import Path
from copy import deepcopy
import ast, io, os, re, sys, tempfile
os.environ.setdefault('MPLCONFIGDIR','/tmp/motor-slide-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'mathtext.fontset':'cm','mathtext.fallback':'cm','svg.fonttype':'path'})
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT=Path(__file__).resolve().parent
NAME='DC Motor Drive, Dual H-Bridge Mechanics, and Open Loop Control'
sys.path.insert(0,str(ROOT.parent/'slide_template'))
import build_template as t
p=Presentation(ROOT.parent/'embedded_software'/'Embedded Software and Deterministic Multitasking.pptx')
original=list(p.slides)
original_ids=list(p.slides._sldIdLst)
RNS='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

# Reuse the presentation helpers without running the Session 03 deck generator.
helper_source=ROOT.parent/'power_architecture_and_adc'/'build_slides.py'
tree=ast.parse(helper_source.read_text())
names={'clone','remove','replace','base','rows','cards','box','photo','math','equations'}
helpers=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
exec(compile(ast.Module(body=helpers,type_ignores=[]),str(helper_source),'exec'),globals())
_photo=photo
asset_dir=Path(tempfile.mkdtemp(prefix='motor-slide-assets-'))
def photo(slide,path,*args,**kwargs):
    # Lossless format conversion for PowerPoint; source artwork is unchanged.
    path=Path(path)
    if path.suffix.lower()=='.webp':
        converted=asset_dir/(path.stem+'.png')
        if not converted.exists():
            with Image.open(path) as im: im.save(converted)
        path=converted
    return _photo(slide,path,*args,**kwargs)
A='01 / Open-Loop Control'
B='02 / DC Motors and Inductive Loads'
C='03 / H-Bridge Switching'
D='04 / Implementation'
DS='https://toshiba.semicon-storage.com/info/datasheet_en_20141001.pdf?did=10660'

def art(section,title,filename,pages,caption,crop=None,dark=False,notes=''):
    s=base(section,title,pages,dark,caption,notes)
    photo(s,ROOT/'img'/filename,.75,2.12,11.8,4.02,crop)
    return s

def table(section,title,headers,data,widths,pages,caption,notes=''):
    s=base(section,title,pages,takeaway=caption,extra=notes)
    x0=.75;y0=2.24;rh=min(.69,3.84/(len(data)+1))
    for i,row in enumerate([headers]+data):
        x=x0
        for j,value in enumerate(row):
            t.rect(s,x,y0+i*rh,widths[j],rh,t.BLUE if i==0 else ('EAF0FA' if i%2 else 'FFFFFF'),t.RULE)
            t.txt(s,x+.12,y0+i*rh+.12,widths[j]-.24,rh-.14,str(value),17 if i==0 else 18,'FFFFFF' if i==0 else t.INK,i==0)
            x+=widths[j]
    return s

def code(title,snippet,pages,caption,notes=''):
    s=base(D+' / Key Firmware',title,pages,True,caption,notes)
    sh=t.codebox(s,.7,2.22,11.95,3.91,snippet,size=21)
    sh.text_frame.margin_left=sh.text_frame.margin_right=Inches(.32)
    sh.text_frame.margin_top=sh.text_frame.margin_bottom=Inches(.23)
    for para in sh.text_frame.paragraphs: para.line_spacing=Pt(21*1.45)
    return s

def bridge(s,x,y,w=4.5,h=3.4,on=(1,4),direction=1,labels=True):
    """Ideal-switch diagram uses the original picture numbering: Q1/Q2 above."""
    def pt(a,b): return x+a*w,y+b*h
    def ln(a,b,c,d,col=t.MUTED,width=1.7,arrow=False):
        t.line(s,*pt(a,b),*pt(c,d),col,width,arrow)
    ln(.18,.05,.82,.05);ln(.18,.95,.82,.95)
    for q,a,b0,b1 in [(1,.18,.05,.5),(2,.82,.05,.5),(3,.18,.5,.95),(4,.82,.5,.95)]:
        mid=(b0+b1)/2;col=t.CYAN if q in on else t.MUTED
        ln(a,b0,a,mid-.07,col);ln(a,mid+.07,a,b1,col)
        ln(a,mid+.07,a if q in on else a+.09,mid-.07,col,2.3)
        if labels:
            xx,yy=pt(a+(.03 if a<.5 else -.13),mid-.14)
            t.txt(s,xx,yy,.55,.3,'Q'+str(q),13,col,font=t.MONO)
    ln(.18,.5,.42,.5,t.CYAN);ln(.58,.5,.82,.5,t.CYAN)
    cx,cy=pt(.42,.5-.08*w/h)
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(cx),Inches(cy),Inches(.16*w),Inches(.16*w))
    sh.fill.solid();sh.fill.fore_color.rgb=t.rgb(t.BG)
    sh.line.color.rgb=t.rgb(t.CYAN);sh.line.width=Pt(2)
    tx=t.txt(s,cx,cy+.025,.16*w,.16*w,'M',20,t.BLUE,True,font=t.MONO)
    tx.text_frame.paragraphs[0].alignment=PP_ALIGN.CENTER
    if direction:
        ln(.32 if direction>0 else .68,.64,.68 if direction>0 else .32,.64,t.PINK,2,True)
    xx,yy=pt(.38,-.09);t.txt(s,xx,yy,1.2,.3,'VM',14,t.CYAN,font=t.MONO)
    xx,yy=pt(.37,.97);t.txt(s,xx,yy,1.4,.3,'GND',13,t.MUTED,font=t.MONO)

def detail(title,crop,notes,caption):
    s=base(D,title,'8',takeaway=caption)
    photo(s,ROOT/'img'/'schematic.png',.7,2.15,7.65,3.98,crop)
    for i,(label,body) in enumerate(notes):
        y=2.3+i*1.23
        t.txt(s,8.7,y,3.8,.32,label,15,t.CYAN,True,font=t.MONO)
        t.txt(s,8.7,y+.38,3.8,.82,body,17)
    return s

# 01 / Cover and contents.
s=clone(0)
for sh in list(s.shapes):
    if sh.has_text_frame:
        if sh.text.startswith('Embedded Software'): replace(sh,'DC Motor Drive\nand Open-Loop\nControl',35)
        elif sh.text.startswith('Scheduling Architecture'): replace(sh,'Dual H-Bridge Mechanics\nand Chassis Motion',23)
        elif sh.text=='Session 02': replace(sh,'Session 04')
    elif sh.left/914400>7.5 and sh.top/914400>1: remove(sh)
photo(s,ROOT/'img'/'h_brdige.webp',7.65,2.15,5.25,3.85)

s=base('00 / Contents','Contents','1–17')
for i,(label,body) in enumerate([
('Open-Loop Control','Commands, actuators, plants, and disturbances'),
('DC Motors','Voltage balance, torque, and inductive loads'),
('H-Bridge Switching','Direction, braking, current decay, and dead time'),
('Implementation','Wire, drive, measure, and debug the chassis')]):
    y=2.3+i*1.03
    t.txt(s,.65,y,.65,.5,f'{i+1:02}',26,t.PINK,font=t.MONO)
    t.txt(s,1.6,y,3.5,.65,label,21,t.BLUE,True)
    t.txt(s,5.25,y+.03,7.3,.65,body,20);t.line(s,1.6,y+.78,12.65,y+.78)

art(A,'From a Command to Physical Motion','control_system_block.excalidraw.png','1–2',
    'The physical load disturbance acts on the motor and chassis.',dark=True,
    notes='Original course artwork retained. Its disturbance arrow points to the controller, but the mechanical load disturbance belongs at the plant. Explain this distinction while walking through the chain.')
table(A,'The Four Functional Blocks',['Block','Role'],[
    ['Reference input','Requested speed or motion from the user or planner.'],
    ['Controller','ESP32 firmware maps the reference to a drive command.'],
    ['Actuator','H-bridge switches electrical power into the motors.'],
    ['Plant','Motors, gearboxes, wheels, and chassis produce motion.']],
    [2.7,9.1],'1–2','A commanded PWM duty is not a measurement of wheel speed.')
equations(A,'Open-Loop Control: No Output Feedback',[
    r'u(t)=f\!\left[r(t)\right]',
    r'D=\frac{|N_{\mathrm{PWM}}|}{255},\qquad 0\leq D\leq1',
    r'V_{\mathrm{avg}}\approx D\,V_M'
],'2','The voltage approximation assumes ideal drive/brake PWM and ignores driver losses.')
rows(A,'Open Loop and Closed Loop',[
('Open loop','The command determines the drive output.\nThere is no measured speed correction.'),
('Closed loop','Measure actual motion and compare it\nwith the desired reference.'),
('Trade-off','Open loop is simple; feedback can correct\nload-dependent speed errors.')],'2','This session establishes the motor-drive layer before adding motion feedback.')
s=equations(A,'A Disturbance Changes the Actual Speed',[
    r'e(t)=r(t)-y(t)',
    r'D_1=D_2,\qquad\omega_1\ne\omega_2\ \text{is possible}'
],'1–2','Friction, battery sag, and unequal wheel loading can change motion at fixed duty.')

# 02 / Motor equations and load behavior.
rows(B,'Keep Logic and Motor Power Separate',[
('ESP32 GPIO','Supplies control signals at 3.3 V logic;\nit is not a motor-power output.'),
('Motor supply','Provides the armature current through\nthe H-bridge and heavy-current return path.'),
('Two failure paths','Excess current can damage GPIO outputs;\ninductive switching can produce voltage spikes.')],'2–3','Connect motors to the driver outputs, with a shared logic ground.')
equations(B,'The Armature Voltage Balance',[
    r'V_{\mathrm{app}}(t)=k_e\omega(t)+I(t)R_a+L_a\frac{dI(t)}{dt}'
],'3','Applied voltage balances back EMF, winding resistance, and inductive voltage.')
table(B,'Read the Motor Model',
    ['Symbol','Meaning','Unit'],[
    ['Vapp','Applied terminal voltage','V'],['ω','Motor-shaft angular speed','rad/s'],
    ['I','Armature current','A'],['Ra / La','Winding resistance / inductance','Ω / H'],
    ['ke / kt','Back-EMF / torque constant','V·s/rad / N·m/A']],
    [1.7,7.4,2.7],'3','Keep shaft speed and gearbox output speed distinct when using motor constants.')
equations(B,'Steady-State Voltage and Torque',[
    r'\frac{dI}{dt}=0\quad\Rightarrow\quad V_{\mathrm{app}}=k_e\omega+IR_a',
    r'\tau=k_tI\quad\Rightarrow\quad I=\frac{\tau}{k_t}'
],'3','Torque is proportional to current; back EMF is proportional to shaft speed.')
equations(B,'Derive the Speed–Torque Relationship',[
    r'V_{\mathrm{app}}=k_e\omega+\frac{R_a}{k_t}\tau',
    r'\omega=\frac{V_{\mathrm{app}}}{k_e}-\frac{R_a}{k_ek_t}\tau',
    r'k_e=k_t\ \text{in consistent SI units}\quad\Rightarrow\quad\omega=\frac{V_{\mathrm{app}}}{k_t}-\frac{R_a}{k_t^2}\tau'
],'3','The slope is −Ra/(ke kt); the squared term applies to kt, not to Ra.')
equations(B,'No-Load and Stall Limits',[
    r'\omega_0\approx\frac{V_{\mathrm{app}}}{k_e}\qquad(\tau\approx0)',
    r'I_{\mathrm{stall}}=\frac{V_{\mathrm{app}}}{R_a}\qquad(\omega=0)',
    r'\tau_{\mathrm{stall}}=k_tI_{\mathrm{stall}}'
],'3–4','Stall is a high-current condition; real no-load current also supplies motor losses.')
art(B,'Speed, Torque, and Mechanical Power','dc_motor_speed_torque_curve.png','4',
    'Original course figure: ideal speed falls as load torque increases.')
equations(B,'Mechanical Power Along the Curve',[
    r'P_{\mathrm{mech}}=\tau\omega',
    r'\tau=\frac{\tau_{\mathrm{stall}}}{2},\quad\omega=\frac{\omega_0}{2}',
    r'P_{\mathrm{max}}=\frac{1}{4}\tau_{\mathrm{stall}}\omega_0'
],'4','This ideal peak-power point is not a continuous operating recommendation.')
equations(B,'Parallel Motors Add Channel Current',[
    r'I_{\mathrm{channel}}=I_{\mathrm{front}}+I_{\mathrm{rear}}',
    r'2\times(0.25\ \text{to}\ 0.40)\,\mathrm{A}=0.50\ \text{to}\ 0.80\,\mathrm{A}',
    r'I_{\mathrm{four\ motors}}=1.00\ \text{to}\ 1.60\,\mathrm{A}'
],'2, 8','Arithmetic uses the PDF’s per-motor example; measure the actual motor demand.')
equations(B,'Inductive Energy and Switching Voltage',[
    r'E_L=\frac{1}{2}L_aI^2',
    r'v_L=L_a\frac{dI}{dt}'
],'4–5','Current cannot change instantaneously: switching must provide a recirculation path.')
rows(B,'Flyback and Current Recirculation',[
('Switch turns off','Stored magnetic energy keeps armature\ncurrent flowing in its original direction.'),
('Current path','Body diodes or driven MOSFETs provide\na path while the winding current decays.'),
('Supply behavior','Some paths return energy to the supply;\nrail voltage and decoupling still matter.')],'4–5','The recirculation path depends on the driver state and current direction.')

# 03 / Original H-bridge drawing, consistent numbering, and switching diagrams.
art(C,'The Four-Switch H-Bridge','h_brdige.webp','5–6',
    'Use the picture numbering: Q1/Q2 are high-side; Q3/Q4 are low-side.',
    notes='The PDF prose labels Q1/Q3 high-side, unlike this image. All tables and editable diagrams in this deck follow the image labels.')
s=base(C,'Forward and Reverse Current Paths','6',takeaway='Select one diagonal pair; motor wiring determines the physical rotation direction.')
bridge(s,1.05,2.55,4.6,3.1,(1,4),1)
bridge(s,7.1,2.55,4.6,3.1,(2,3),-1)
t.txt(s,1.2,2.13,4.6,.32,'FORWARD / Q1 + Q4',15,t.CYAN,font=t.MONO)
t.txt(s,7.25,2.13,4.6,.32,'REVERSE / Q2 + Q3',15,t.PINK,font=t.MONO)
table(C,'Ideal Switch States',
    ['Mode','Q1','Q2','Q3','Q4','Motor state'],[
    ['Forward','ON','OFF','OFF','ON','+VM'],
    ['Reverse','OFF','ON','ON','OFF','−VM'],
    ['Low-side brake','OFF','OFF','ON','ON','Terminals shorted'],
    ['Coast command','OFF','OFF','OFF','OFF','Outputs high-Z']],
    [2.7,1.15,1.15,1.15,1.15,4.5],'6–7','These are transistor states, not the integrated driver’s input truth table.')
rows(C,'Braking and Coasting Are Different',[
('Dynamic braking','Both motor terminals are tied together.\nGenerated current opposes the ongoing motion.'),
('Coasting','Outputs are high impedance; the rotor slows\nthrough mechanical and electrical losses.'),
('During PWM','Current decay describes the winding current\nduring the inactive part of each PWM cycle.')],'6–7','Do not use “brake/coast” and “fast/slow decay” as interchangeable names.')
rows(C,'Slow and Fast Current Decay',[
('Slow decay','Shorted-terminal recirculation usually applies\na relatively small opposing winding voltage.'),
('Fast decay','A path through the opposite diagonal or\ndiodes applies a larger opposing voltage.'),
('Practical effect','The off-state changes current ripple,\nresponse speed, and the duty-to-speed relation.')],'7','Include back EMF and resistance when analyzing a rotating motor.')
art(C,'Shoot-Through: A Supply Short Circuit','shoot_through.gif','7',
    'Never turn on the high-side and low-side switches of the same leg together.')
s=base(C,'Dead Time Between Complementary Switches','8',takeaway='The integrated driver inserts dead time; motor reversal is a separate current transient.',extra='TB6612FNG datasheet confirms internal dead time. Avoid the PDF’s universal immunity claim and generic timing inequality. '+DS)
for y,label,col in [(3.05,'HIGH-SIDE',t.BLUE),(4.8,'LOW-SIDE',t.CYAN)]:
    t.txt(s,.9,y-.12,2,.5,label,15,col,font=t.MONO)
    t.line(s,3.1,y+.5,12.1,y+.5,t.RULE,1)
t.line(s,3.1,2.65,6.3,2.65,t.BLUE,2.5);t.line(s,6.3,2.65,6.3,3.55,t.BLUE,2.5);t.line(s,6.3,3.55,12.1,3.55,t.BLUE,2.5)
t.line(s,3.1,5.3,7.25,5.3,t.CYAN,2.5);t.line(s,7.25,5.3,7.25,4.4,t.CYAN,2.5);t.line(s,7.25,4.4,12.1,4.4,t.CYAN,2.5)
t.line(s,6.3,3.95,7.25,3.95,t.PINK,1.8,True)
t.txt(s,7.65,3.75,4,.5,'Both switches OFF',19,t.PINK)
table(C,'TB6612FNG: Command the Actual IC',
    ['STBY','IN1','IN2','PWM','Output mode'],[
    ['LOW','X','X','X','Standby / high-Z'],
    ['HIGH','HIGH','LOW','HIGH','Forward polarity'],
    ['HIGH','LOW','HIGH','HIGH','Reverse polarity'],
    ['HIGH','HIGH','HIGH','X','Short brake'],
    ['HIGH','LOW','LOW','HIGH','Stop / high-Z'],
    ['HIGH','HIGH','LOW','LOW','Short brake (PWM off)']],
    [1.35,1.35,1.35,1.35,6.3],'6–8, 11–12','X = either level. Use the actual driver table when choosing stop and PWM behavior.',DS)

# 04 / User schematic, detail crops, pin mapping, and motor-rating checks.
art(D,'The Complete Motor-Drive Schematic','schematic.png','8',
    'Original drawing: follow net labels between ESP32, driver, and the two motor pairs.')
detail('Schematic: ESP32 Control Signals',(.085,.015,.307,.60),[
    ('CHANNEL A','PWMA → GPIO 18\nAIN1/AIN2 → 25/27'),
    ('CHANNEL B','PWMB → GPIO 19\nBIN1/BIN2 → 26/33'),
    ('ENABLE','STBY → GPIO 5\nCommon GND reference')],
    'GPIO numbers identify ESP32 signals; they are not the driver IC’s package pin numbers.')
detail('Schematic: TB6612FNG Connections',(.77,.015,.995,.60),[
    ('CONTROL','Direction inputs, PWM,\nand active-high STBY.'),
    ('SUPPLIES','VCC is logic supply;\nVM is motor supply.'),
    ('OUTPUTS','AO1/AO2 → left pair;\nBO1/BO2 → right pair.')],
    'Connect power ground and logic ground to the common reference.')
detail('Schematic: Two Motors per Channel',(.003,.618,.58,.982),[
    ('LEFT PAIR','M1 and M3 share\nthe channel A outputs.'),
    ('RIGHT PAIR','M2 and M4 share\nthe channel B outputs.'),
    ('CHECK POLARITY','Paired wheels must\npropel the same side.')],
    'Parallel motors share voltage; their currents add at the driver channel.')
rows(D,'Resolve the Supply Labels Before Wiring',[
    ('Original drawing','The buck symbols are labeled 3.3 V and 12 V;\nthe text describes 5 V VIN and a 6 V motor rail.'),
    ('Logic supply','Use a compatible logic supply for 3.3 V\nESP32 outputs; distinguish VCC from VM.'),
    ('Motor rating','The notes list 5 V gearmotors. Confirm their\nallowed voltage before using the 6 V example.')],'8, 16','Set the rail to suit the actual motor; lower duty still applies full-voltage PWM pulses.',extra='Schematic/procedure mismatch made explicit. TB6612FNG logic threshold is relative to VCC. '+DS)
table(D,'Firmware Pin Map',
    ['Function','Left / Channel A','Right / Channel B'],[
    ['PWM','GPIO 18 / LEDC 0','GPIO 19 / LEDC 1'],
    ['Direction IN1','GPIO 25','GPIO 26'],
    ['Direction IN2','GPIO 27','GPIO 33'],
    ['Shared enable','STBY: GPIO 5','STBY: GPIO 5'],
    ['Supporting I/O','Heartbeat: GPIO 4','Battery ADC: GPIO 32']],
    [3.0,4.4,4.4],'8–10','The firmware uses two independent PWM channels at 20 kHz and 8-bit resolution.')
s=base(D,'Signed Commands Produce Chassis Motion','12–13',takeaway='Check the physical wheel direction before interpreting command signs.')
for i,(label,left,right) in enumerate([('FORWARD',1,1),('REVERSE',-1,-1),('SPIN LEFT',-1,1)]):
    x=1.1+i*4.1
    t.txt(s,x,2.4,3.3,.4,label,17,t.CYAN,font=t.MONO)
    for dx,direction in [(.4,left),(2.5,right)]:
        t.rect(s,x+dx,3.65,.35,1.25,t.INK)
        t.line(s,x+dx+.17,3.35 if direction>0 else 5.2,x+dx+.17,2.95 if direction>0 else 5.6,t.PINK,2.4,True)
    t.line(s,x+.75,4.27,x+2.5,4.27,t.CYAN,2)
    t.txt(s,x,5.75,3.5,.3,('L + / R +' if left==right==1 else 'L − / R −' if left==right else 'L − / R +'),15,t.BLUE,font=t.MONO)
equations(D,'Calculate Duty and Expected Average Voltage',[
    r'D=\frac{180}{255}\approx0.7059=70.59\%',
    r'V_{\mathrm{avg}}\approx0.7059\times6\,\mathrm{V}\approx4.24\,\mathrm{V}',
    r'N=-180\quad\Rightarrow\quad V_{\mathrm{avg}}\approx-4.24\,\mathrm{V}'
],'2, 13, 16','Ideal 6 V reference example; driver losses and meter response change measured values.')
table(D,'The Source Demo: An Eight-Second Sequence',
    ['Time in cycle','Left duty','Right duty','Motion'],[
    ['0–2 s','+180','+180','Forward'],
    ['2–4 s','−180','−180','Reverse'],
    ['4–6 s','−150','+150','Spin left'],
    ['6–8 s','0','0','Stop']],
    [3.1,2.0,2.0,4.7],'13','This is a step sequence, not a ramp. Test one mode at a time before sequencing.')
cards(D,'Keep Motion and Logging at Different Rates',[
    ('MOTION','100 Hz','Apply left/right\ncommands every 10 ms.'),
    ('TELEMETRY','10 Hz','Report duty, battery,\nand driver state.'),
    ('HEARTBEAT','1 Hz task','Toggle the status LED\nevery second.')],'13–16','Hardware PWM runs independently at 20 kHz.')

# Key excerpts only; 21-point code and generous line spacing.
code('Start with the Driver Disabled',
'''pinMode(PIN_STBY, OUTPUT);
digitalWrite(PIN_STBY, LOW);

digitalWrite(PIN_AIN1, LOW);
digitalWrite(PIN_AIN2, LOW);
digitalWrite(PIN_BIN1, LOW);
digitalWrite(PIN_BIN2, LOW);''','10',
'Configure direction pins as outputs first; keep STBY low during initialization.')
code('Attach the Two PWM Channels',
'''bool left_ok = ledcAttachChannel(
  PIN_PWMA, 20000, 8, LEDC_CHANNEL_LEFT);
bool right_ok = ledcAttachChannel(
  PIN_PWMB, 20000, 8, LEDC_CHANNEL_RIGHT);
if (!left_ok || !right_ok) return false;

ledcWrite(PIN_PWMA, 0);
ledcWrite(PIN_PWMB, 0);''','10–11',
'Enable STBY only after PWM initialization succeeds and both duties are zero.')
code('Positive Command: Forward Polarity',
'''duty_count = constrain(duty_count, -255, 255);

if (duty_count > 0) {
  digitalWrite(PIN_AIN1, HIGH);
  digitalWrite(PIN_AIN2, LOW);
  ledcWrite(PIN_PWMA, uint8_t(duty_count));
}''','11',
'Inside setLeftMotorSpeed(): magnitude controls duty; direction inputs set polarity.')
code('Negative Command: Reverse Polarity',
'''else if (duty_count < 0) {
  digitalWrite(PIN_AIN1, LOW);
  digitalWrite(PIN_AIN2, HIGH);

  ledcWrite(PIN_PWMA, uint8_t(-duty_count));
}''','11–12',
'Mirror the same logic for channel B; manage reversal transients before high-load tests.')
code('Zero Command: Explicit Short Brake',
'''else {
  digitalWrite(PIN_AIN1, HIGH);
  digitalWrite(PIN_AIN2, HIGH);
  ledcWrite(PIN_PWMA, 0);
}''','11–12',
'TB6612FNG: both direction inputs HIGH explicitly select short brake.',
notes='Corrected teaching excerpt: source uses both inputs LOW and PWM zero while calling it fast-decay braking. Use the documented HIGH/HIGH short-brake command with STBY high. '+DS)
code('Apply Independent Left and Right Commands',
'''void driveRobot(int16_t left, int16_t right) {
  left_command_duty = constrain(left, -255, 255);
  right_command_duty = constrain(right, -255, 255);

  setLeftMotorSpeed(left_command_duty);
  setRightMotorSpeed(right_command_duty);
}''','12',
'Store the bounded commands so telemetry agrees with the PWM values sent to the driver.')
code('Run the Motion Task at 100 Hz',
'''if (uint32_t(current_us - last_motion_time_us)
    >= INTERVAL_MOTION_US) {

  last_motion_time_us += INTERVAL_MOTION_US;
  task_motion_control();
}''','15–16',
'Use the existing 10 Hz telemetry and 1 Hz heartbeat checks alongside this one.')

rows(D,'Bench Setup Before the First Motion',[
    ('Power disconnected','Verify common ground, wiring polarity,\nand that no supply rail has a persistent short.'),
    ('Wheels clear','Secure the chassis with wheels off the bench.\nKeep access to the power disconnect.'),
    ('One step at a time','Start at low duty on one channel; confirm\nboth paired wheels move in the intended direction.')],'8, 16','Stop before reversing during initial tests; build up to the source demonstration.')
rows(D,'Verify Logic Supply, Motor Supply, and Enable',[
    ('Logic rail','The course target is 5.00 V ± 0.05 V\nat ESP32 VIN; check driver VCC separately.'),
    ('Motor rail','Measure VM relative to power ground.\nUse the voltage appropriate to the actual motors.'),
    ('Standby input','STBY low disables the outputs.\nConfirm the intended enable level at the driver.')],'16','Check rail voltage under load, not only with the motors disconnected.')
rows(D,'Measure Across the Motor Outputs',[
    ('Probe location','Measure between OUT1 and OUT2,\nnot only from either output to ground.'),
    ('Polarity','The meter should change sign when the\ncommand direction is reversed.'),
    ('Magnitude','At duty 180 and a 6 V reference rail,\nthe ideal average is about ±4.24 V.')],'16','PWM measurements depend on the meter; a scope shows the actual switching waveform.')
rows(D,'Debugging: No Motor Motion',[
    ('Start with STBY','Check the enable pin at the driver,\nthen check firmware initialization.'),
    ('Check VM + GND','Verify supply, fuse, terminal connections,\nand ground continuity.'),
    ('Then check inputs','Verify direction levels and PWM at the IC.\nCheck output wiring and thermal state next.')],'16–17','A zero output alone does not prove the driver is damaged.')
rows(D,'Debugging: Wrong Direction or Uneven Motion',[
    ('One wheel fights','Check polarity of the two motors wired\nin parallel on that channel.'),
    ('Chassis curves','Equal duty does not guarantee equal speed;\nload, motor tolerances, and friction can differ.'),
    ('Reset or sag','Inspect the power and return paths;\nobserve supply voltage during motor startup.')],'1–2, 8, 16','Separate wiring problems from the inherent limits of open-loop speed control.')
rows(D,'Before Moving to Closed-Loop Control',[
    ('Electrical behavior','Both channels respond to signed duty\nand have a verified stop/standby state.'),
    ('Physical behavior','Wheel polarity and chassis motion agree\nwith the intended command convention.'),
    ('Next measurement','Encoders will measure actual motion\nso the controller can correct speed error.')],'1–2, 8, 16–17','Command → driver → motor is now the foundation for feedback control.')

# Exactly the four URLs supplied by the user; no substituted destinations.
refs=re.findall(r'^- \[(.*?)\]\((.*)\)$',(ROOT/(NAME+'.md')).read_text(),re.M)
assert len(refs)==4
s=base('>_ KEEP EXPLORING ^_^','References','17')
for i,(label,url) in enumerate(refs):
    label=[
      'Espressif Systems — LED Control (LEDC)\nArduino-ESP32 API documentation',
      'Texas Instruments — Motor Drivers Overview',
      'Making Embedded Systems: Design Patterns for Great Software\nElecia White',
      'Modern Robotics: Mechanics, Planning, and Control\nKevin M. Lynch and Frank C. Park'][i]
    y=2.21+i*1.04
    t.txt(s,.85,y,.6,.4,f'{i+1:02}',23,t.PINK,font=t.MONO)
    sh=t.txt(s,1.7,y,10.65,.86,label,19,t.BLUE)
    for para in sh.text_frame.paragraphs:
        for run in para.runs: run.hyperlink.address=url;run.font.underline=True
    t.line(s,1.7,y+.93,12.55,y+.93)
s.notes_slide.notes_text_frame.text='Exact reference URLs from the user’s Markdown. TI label reflects the actual overview-page destination. Driver behavior was cross-checked against the TB6612FNG datasheet: '+DS

# Closing: actual switching diagram rather than three rectangular labels.
s=clone(0)
for sh in list(s.shapes):
    if 1<sh.top/914400<7:remove(sh)
t.txt(s,.6,1.5,12,.4,'SESSION 04 / DC MOTOR DRIVE & OPEN-LOOP CONTROL',13,t.CYAN,font=t.MONO)
t.txt(s,.6,2.3,12,1,'Thank you!',48,t.BLUE,True,font=t.MONO)
t.txt(s,.6,3.4,12,.6,'Questions & discussion',28)
bridge(s,1.15,4.25,3.4,1.9,(1,4),1,False)
t.line(s,4.65,5.2,7.1,5.2,t.PINK,2,True)
t.txt(s,5.0,4.62,2.1,.4,'DRIVE',15,t.CYAN,font=t.MONO)
for x in [8.05,10.85]:
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(4.65),Inches(1.1),Inches(1.1))
    sh.fill.background();sh.line.color.rgb=t.rgb(t.CYAN);sh.line.width=Pt(2.4)
    t.line(s,x+.55,4.9,x+.55,5.45,t.CYAN,2)
    t.line(s,x+.32,4.35,x+.78,4.35,t.PINK,2,True)
t.line(s,9.15,5.2,10.85,5.2,t.CYAN,2)
t.txt(s,8.35,6.1,4,.35,'OBSERVE THE MOTION',14,t.CYAN,font=t.MONO)

for sid in original_ids:
    p.part.drop_rel(sid.rId);p.slides._sldIdLst.remove(sid)
for i,s in enumerate(p.slides,1):
    dark=s.background.fill.fore_color.rgb==t.rgb(t.NAVY)
    t.txt(s,12.2,7.14,.5,.19,f'{i:02}',9,'828BB8' if dark else t.MUTED,font=t.MONO)
p.core_properties.title=NAME
p.core_properties.subject='DCLab Control System Crash Course / Session 04'
p.core_properties.author='DCLab'
p.save(ROOT/(NAME+'.pptx'))
print(f'Saved {len(p.slides)} slides: {ROOT/(NAME+".pptx")}')
