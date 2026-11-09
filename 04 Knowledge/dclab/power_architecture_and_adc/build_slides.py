"""Build Session 03 using the existing Session 02 artwork and course PDF.

Requires python-pptx, Pillow and Pygments. Run from any directory.
"""
from pathlib import Path
from copy import deepcopy
import sys
import re
import io
import subprocess
import tempfile
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/power-slides-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Use LaTeX's Computer Modern fonts for equations, including math in plot labels.
# Store SVG glyph outlines so PowerPoint does not substitute a system font.
matplotlib.rcParams.update({
    'mathtext.fontset': 'cm',
    'mathtext.fallback': 'cm',
    'svg.fonttype': 'path',
})
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'slide_template'))
import build_template as t
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent
NAME = 'Power Architecture, Dual Buck Calibration, and Analog Battery Sensing'
SOURCE = ROOT.parent / 'embedded_software' / 'Embedded Software and Deterministic Multitasking.pptx'
p = Presentation(SOURCE)
original = list(p.slides)
original_ids = list(p.slides._sldIdLst)
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
ADC_URL = 'https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html'
GPIO_URL = 'https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html'

def clone(index):
    src = original[index]
    s = p.slides.add_slide(src.slide_layout)
    for sh in list(s.shapes):
        sh._element.getparent().remove(sh._element)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = src.background.fill.fore_color.rgb
    for sh in src.shapes:
        el = deepcopy(sh._element)
        for node in el.iter():
            for key, val in list(node.attrib.items()):
                if key.startswith(RNS):
                    rel = src.part.rels[val]
                    node.set(key, s.part.relate_to(rel.target_ref if rel.is_external else rel.target_part, rel.reltype, rel.is_external))
        s.shapes._spTree.insert_element_before(el, 'p:extLst')
    return s

def remove(sh):
    sh._element.getparent().remove(sh._element)

def replace(sh, value, size=None):
    para = sh.text_frame.paragraphs[0]
    r = para.runs[0] if para.runs else para.add_run()
    style = deepcopy(r._r.rPr) if r._r.rPr is not None else None
    sh.text_frame.clear()
    r = sh.text_frame.paragraphs[0].add_run(); r.text = value
    if style is not None: r._r.insert(0, style)
    if size: r.font.size = Pt(size)

def base(section, title, pages, dark=False, takeaway='', extra=''):
    s = clone(15 if dark else 3)
    s.background.fill.fore_color.rgb = t.rgb(t.NAVY if dark else t.BG)
    for sh in list(s.shapes):
        y = sh.top / 914400
        if 2.05 < y < 7.0: remove(sh)
        elif sh.has_text_frame and abs(y - .4) < .03: replace(sh, section)
        elif sh.has_text_frame and abs(y - .99) < .03: replace(sh, title, 28 if len(title)<49 else 25)
    if not dark:
        for sh in s.shapes:
            y = sh.top / 914400
            if sh.has_text_frame:
                color = t.CYAN if y < .8 else t.BLUE if y < 2 else t.MUTED
                for para in sh.text_frame.paragraphs:
                    for run in para.runs: run.font.color.rgb = t.rgb(color)
            elif sh.height / 914400 < .02:
                sh.line.color.rgb = t.rgb(t.RULE)
    if takeaway: t.txt(s,.85,6.25,11.65,.48,takeaway,18,'48CAE4' if dark else t.CYAN)
    t.txt(s,.85,6.84,11.5,.16,'Source: course PDF, pp. '+pages,8.5,'828BB8' if dark else t.MUTED,font=t.MONO)
    s.notes_slide.notes_text_frame.text = f'Reference: {NAME}.pdf, pages {pages}.\n{extra}'
    return s

def rows(section,title,items,pages,takeaway='',extra=''):
    s=base(section,title,pages,takeaway=takeaway,extra=extra)
    for i,(label,body) in enumerate(items):
        y=2.35+i*1.18
        t.rect(s,.75,y,11.83,1.04,'EAF0FA')
        t.txt(s,.96,y+.17,3.05,.72,label,22,t.BLUE,True)
        t.txt(s,4.25,y+.15,8.0,.78,body,21)
    return s

def cards(section,title,items,pages,takeaway='',extra=''):
    s=base(section,title,pages,True,takeaway,extra)
    t.rect(s,.65,2.3,12.02,3.88,'16161E','343B54')
    for i,(label,value,body) in enumerate(items):
        x=.95+i*4.02
        t.txt(s,x,2.58,3.4,.35,label,13,'48CAE4',font=t.MONO)
        t.txt(s,x,3.18,3.4,.9,value,27,t.PALE,True)
        t.txt(s,x,4.35,3.4,1.6,body,20,t.PALE)
    return s

def code(title,source,pages,takeaway,extra=''):
    s=base('04 / Implementation / Firmware',title,pages,True,takeaway,extra)
    t.codebox(s,.7,2.28,11.95,3.87,source,size=18)
    return s

def box(s,x,y,w,h,label,color=t.CYAN,dark=False,size=19):
    t.rect(s,x,y,w,h,'202233' if dark else 'EAF0FA',color)
    sh=t.txt(s,x+.12,y+.15,w-.24,h-.18,label,size,t.PALE if dark else t.INK,True,font=t.MONO)
    for para in sh.text_frame.paragraphs: para.alignment=PP_ALIGN.CENTER

A='01 / Power Architecture'
B='02 / Buck Calibration'
C='03 / Analog Battery Sensing'
D='04 / Implementation'

# Cover retains the logos, split layout, typography, footer and session marker.
s=clone(0)
for sh in list(s.shapes):
    if sh.has_text_frame:
        if sh.text.startswith('Embedded Software'): replace(sh,'Power Architecture\nand ADC',37)
        elif sh.text.startswith('Scheduling Architecture'): replace(sh,'Dual Buck Calibration and\nAnalog Battery Sensing',23)
        elif sh.text=='Session 02': replace(sh,'Session 03')
    elif sh.left/914400>7.5 and sh.top/914400>1: remove(sh)
box(s,8.15,2.15,4.35,.85,'4S BATTERY / 12–16.8 V',size=17)
t.line(s,10.32,3,10.32,3.4,t.CYAN,2)
t.line(s,8.85,3.4,11.85,3.4,t.CYAN,2)
for x in [8.85,11.85]: t.line(s,x,3.4,x,3.75,t.CYAN,2,True)
box(s,7.7,3.75,2.6,1.1,'5 V\nLOGIC',size=20)
box(s,10.65,3.75,2.1,1.1,'6 V\nMOTORS',t.PINK,size=20)
t.txt(s,8.05,5.3,4.7,.65,'REGULATE / MEASURE / FILTER',13,t.MUTED,font=t.MONO)
s.notes_slide.notes_text_frame.text=f'Session 03. Based on {NAME}.pdf. Style inherited from Session 02 and the shared DC Lab template.'

s=base('00 / Contents','Contents','1–19')
for i,(label,body) in enumerate([('Power Architecture','Separate supply rails and shared return paths'),('Buck Calibration','Set and verify the 5 V and 6 V outputs'),('Analog Sensing','Scale, convert, and filter battery voltage'),('Implementation','Integrate firmware, measure, and debug')]):
    y=2.3+i*1.03
    t.txt(s,.65,y,.65,.5,f'{i+1:02}',26,t.PINK,font=t.MONO)
    t.txt(s,1.6,y,3.5,.65,label,21,t.BLUE,True)
    t.txt(s,5.25,y+.03,7.3,.65,body,20)
    t.line(s,1.6,y+.78,12.65,y+.78)

rows(A,'One Battery, Two Different Loads',[
('Digital logic','ESP32 and sensors need a stable supply\nfor computation, sensing, and communication.'),
('Motor drive','Starting, reversing, and stalling motors\nproduce large changes in current demand.'),
('Shared supply risk','Voltage sag and ground bounce can disturb\nmeasurements or cause the MCU to reset.')],'1–2','Design the power path around the load behavior.')

s=base(A,'Separate Rails, Common Ground','1–2',takeaway='Separate positive rails; return each branch to the ground bus.',extra='The buck modules share a battery and ground. They do not provide galvanic isolation or guarantee zero coupled noise. The source diagram is redrawn to avoid joining the 5 V and 6 V outputs.')
box(s,.8,3.2,2.25,1.1,'4S BATTERY\n12–16.8 V',size=17)
box(s,3.7,3.35,1.65,.8,'FUSE',size=18)
t.line(s,3.05,3.75,3.7,3.75,t.PINK,2,True)
t.line(s,5.35,3.75,5.85,3.75,t.PINK,2)
t.line(s,5.85,2.85,5.85,4.65,t.PINK,2)
for y,label,load,col in [(2.35,'BUCK 1 / 5 V','ESP32 VIN\n5 V sensors',t.CYAN),(4.15,'BUCK 2 / 6 V','Driver VM\nMotors',t.PINK)]:
    t.line(s,5.85,y+.5,6.35,y+.5,col,2,True)
    box(s,6.35,y,2.8,1,label,col,size=17)
    t.line(s,9.15,y+.5,9.65,y+.5,col,2,True)
    box(s,9.65,y,2.9,1,load,col,size=17)
t.line(s,1.9,5.65,11.8,5.65,t.MUTED,2)
for x,y in [(1.9,4.3),(7.75,5.15),(11.1,5.15)]: t.line(s,x,y,x,5.65,t.MUTED,1.5)
for x in [7.75,11.1]:
    t.line(s,x,3.35,x,3.62,t.MUTED,1.5)
    for y,w in [(3.62,.42),(3.68,.28),(3.74,.12)]:
        t.line(s,x-w/2,y,x+w/2,y,t.MUTED,1.2)
    t.txt(s,x+.3,3.57,.8,.25,'GND',10,t.MUTED,font=t.MONO)
t.txt(s,3.1,5.8,8,.3,'COMMON GROUND / separate motor and logic return wiring',13,t.MUTED,font=t.MONO)

cards(A,'The 4S Battery Operating Range',[
('FULLY CHARGED','16.8 V','4 × 4.2 V\nMaximum pack voltage.'),
('NOMINAL','14.8 V','4 × 3.7 V\nNominal rating, not a\nconstant voltage.'),
('LAB THRESHOLD','12.0 V','4 × 3.0 V\nPack-level low-voltage\nwarning threshold.')],'2','Pack voltage alone does not reveal individual cell imbalance.',extra='Threshold follows the course example; suitable cell-level protection and charging must match the actual pack. Do not interpret 12 V as a universal 0% state of charge.')

cards(A,'Buck Regulator Input Headroom',[
('MOTOR OUTPUT','6.0 V','Target voltage at the\nmotor driver supply.'),
('EXAMPLE HEADROOM','1.5 V','Approximate allowance\nused in the course.\nCheck the actual module.'),
('MINIMUM INPUT','7.5 V','6.0 V + 1.5 V\nThe 12 V pack threshold\nleaves nominal margin.')],'2','Also check voltage sag, module current limits, and temperature.')

rows(A,'Protection and Return Paths',[
('Fuse near battery','The reference uses a 2 A inline fuse.\nConfirm its rating against wiring and load demand.'),
('Star ground','Return high motor currents directly to the\nmain terminal bus using suitable heavy wire.'),
('Logic wiring','Keep motor current out of breadboard tracks\nand thin logic jumpers; use local decoupling.')],'2–3','A fuse limits fault energy; its clearing time depends on fault current.',extra='The PDF’s universal millisecond clearing and guaranteed fire-prevention claims are not repeated. 2 A is a reference design value, not a substitute for load and fuse-curve verification.')

rows(B,'Before Applying Power',[
('Disconnect loads','Keep ESP32 VIN and motor-driver VM\ndisconnected until both rails are adjusted.'),
('Inspect + measure','With power OFF, verify polarity, fuse,\nground continuity, and no persistent rail short.'),
('Identify outputs','Label Buck 1 = 5 V and Buck 2 = 6 V.\nUse adjustable modules for these setpoints.')],'7','Use resistance and continuity modes only on an unpowered circuit.',extra='Corrects the duplicated Buck 2 label and the contradictory fixed-output buck symbols in the PDF. Use adjustable converter modules with appropriate input/current ratings.')

rows(B,'Calibrate the Two Buck Outputs',[
('1 / Battery input','Measure pack DC voltage at the main bus;\nverify polarity and compare the battery display.'),
('2 / Logic rail','Probe Buck 1 OUT+ to OUT−. Adjust the\ntrimmer carefully until the meter reads 5.00 V.'),
('3 / Motor rail','Probe Buck 2 OUT+ to OUT−. Adjust to 6.00 V.\nCompare both displays with the multimeter.')],'7','Adjust while watching the meter; trimmer direction varies by module.',extra='The PDF’s ±5 V tolerance is a typo and is omitted. The multimeter is the calibration reference; the displays are secondary indicators.')

rows(B,'Verify Before Connecting the Loads',[
('Power OFF','Verify that 5 V and 6 V positives are not\naccidentally tied together; grounds are shared.'),
('Reconnect','Connect each load to its labeled rail.\nRecheck polarity before applying power.'),
('Power ON','Measure both rails under load and during\nmotor startup; investigate sag or overheating.')],'7–9','A resistance reading alone does not prove electrical isolation.',extra='The PDF asks for >100 kΩ between rails as proof of isolation. These non-isolated buck modules share ground; internal paths and capacitors affect resistance readings. Check wiring and outputs instead.')

s=base(C,'Scale the Battery Voltage Safely','3–5',takeaway='The ADC reads the divider midpoint, never the raw battery voltage.')
box(s,1.0,2.4,2.8,.7,'VBAT / 12–16.8 V',size=17)
t.line(s,2.4,3.1,2.4,3.45,t.CYAN,2)
box(s,1.7,3.45,1.4,.65,'100 kΩ',size=16)
t.line(s,2.4,4.1,2.4,4.55,t.CYAN,2)
t.line(s,2.4,4.32,4.9,4.32,t.CYAN,2,True)
t.txt(s,3.2,3.85,2.3,.35,'Vpin → GPIO 32',15,t.CYAN,font=t.MONO)
box(s,1.7,4.55,1.4,.65,'22 kΩ',size=16)
t.line(s,2.4,5.2,2.4,5.55,t.CYAN,2)
t.line(s,2.0,5.55,2.8,5.55,t.CYAN,2)
t.txt(s,1.8,5.65,2,.35,'GND',16,t.MUTED,font=t.MONO)
t.txt(s,6.1,2.65,6.25,1.05,'Vpin = Vbat × Rbottom\n              / (Rtop + Rbottom)',23,t.BLUE,font=t.MONO)
t.txt(s,6.1,4.0,6.1,.6,'Kdiv = 22 / 122 ≈ 0.180328',22,t.CYAN,font=t.MONO)
t.txt(s,6.1,5.1,5.8,.9,'Use precision resistors and a shared\nground reference for the measurement.',21)

cards(C,'Check the Divider at Both Limits',[
('AT 16.8 V','3.030 V','16.8 × 22 / 122\nNominal maximum\nADC input voltage.'),
('AT 12.0 V','2.164 V','12.0 × 22 / 122\nADC input at the\nlab warning threshold.'),
('DIVIDER CURRENT','138 µA','16.8 V / 122 kΩ\nSmall continuous drain;\nit is not zero.')],'4–5','Verify the assembled divider with a meter before attaching the ADC.')

rows(C,'Choose an ADC1 Input',[
('GPIO 32','ADC1 channel 4; a general-purpose I/O.\nConfigure it as an input for battery sensing.'),
('GPIO 34','ADC1 channel 6; input-only.\nNo internal pull-up or pull-down resistor.'),
('Wi-Fi coexistence','Prefer ADC1 for this classic ESP32 design.\nADC2 is shared with the Wi-Fi subsystem.')],'5','Pin mappings differ across ESP32 variants; check the actual board.',extra='Correction: GPIO32 is not input-only. Official GPIO reference: '+GPIO_URL)

cards(C,'ADC Resolution and Input Range',[
('RESOLUTION','12 bits','2¹² = 4096 levels\nRaw codes: 0–4095.'),
('ATTENUATION','ADC_11db','Classic ESP32 documented\nrange: about 0.15–3.10 V.\nCheck device variant.'),
('PRACTICAL CHECK','3.030 V','The nominal full-pack\ndivider voltage is close\nto the top of this range.')],'5–6','Resolution, measurable range, and accuracy are different properties.',extra='Corrects 4086 to 4096. The 3.3 V ideal conversion in the PDF is not a calibrated ESP32 transfer function. Verify resistor tolerance and usable range. Official ADC reference: '+ADC_URL)

s=base(C,'Reconstruct the Battery Voltage','6, 11–12',True,'Use calibrated millivolts, then undo the external divider.',extra='The raw-count equation in the PDF is a conceptual ideal-ADC estimate. The supplied firmware uses analogReadMilliVolts(). Official ADC API: '+ADC_URL)
t.txt(s,.95,2.55,11.5,.7,'Kinverse = (100 kΩ + 22 kΩ) / 22 kΩ',27,t.PALE,font=t.MONO)
t.txt(s,.95,3.5,11.5,.65,'Vbat = Vpin × 5.54545',30,'48CAE4',font=t.MONO)
t.txt(s,.95,4.65,11.4,1,'Example: 2669 mV → 2.669 V\n2.669 × 5.54545 ≈ 14.80 V',25,t.PALE,font=t.MONO)

rows(C,'Why Raw Voltage Readings Move',[
('Switching ripple','Buck converters inject switching components\nonto the supply and ground network.'),
('Motor transients','Commutation and changing load current cause\nspikes, voltage sag, and ground bounce.'),
('Measurement chain','ADC noise, divider tolerances, and wiring\nadd variation to the sampled voltage.')],'6','Improve wiring first; filtering cannot repair a bad electrical connection.')

s=base(C,'Exponential Moving Average (EMA)','6–7, 12',True,'Prime the filter with the first sample so it does not start at zero.')
t.txt(s,.95,2.5,11.5,.8,'y[k] = α·x[k] + (1 − α)·y[k−1]',29,t.PALE,font=t.MONO)
t.txt(s,.95,3.65,11.3,.8,'New sample x[k]     Previous result y[k−1]',22,'48CAE4',font=t.MONO)
t.txt(s,.95,4.75,11.4,1.05,'Course firmware: α = 0.15\n15% new measurement + 85% previous result',25,t.PALE,font=t.MONO)

cards(C,'Choose the Smoothing Coefficient',[
('α = 1.00','Fast / noisy','Output equals the\nnewest sample.\nNo smoothing.'),
('α = 0.15','Lab starting point','Balances smoothing\nand responsiveness at\nthe 10 Hz sample rate.'),
('α = 0.01','Slow / smooth','Strong smoothing\nwith substantial lag\nafter voltage changes.')],'6–7','The response depends on both α and the sampling interval.')

rows(C,'Battery Percentage and Low Voltage',[
('Voltage indicator','Clamp 100 × (Vfiltered − 12.0) / 4.8\nto the range 0–100%.'),
('Low-voltage flag','The course firmware asserts its warning\nwhen filtered voltage is below 12.0 V.'),
('Interpretation','Load and cell chemistry affect voltage.\nThis percentage is not a true SOC estimate.')],'12–15','The example reports an alarm; it does not implement a motor shutdown.',extra='A pack-level warning is not a replacement for cell-level protection. Filter delay also delays alarm response.')

rows(D,'Connect the Measurement Chain',[
('Power','Buck 1 → ESP32 VIN / suitable 5 V loads.\nBuck 2 → motor-driver VM terminals.'),
('Sense','Battery → 100 kΩ → GPIO 32 midpoint.\nMidpoint → 22 kΩ → common ground.'),
('Outputs + serial','GPIO 18: PWM; GPIO 4: heartbeat LED.\nUse current limiting for LEDs; serial: 115200 baud.')],'8–10, 15–17','Keep the 5 V and 6 V rails separate and verify the board power input.',extra='Check the development board’s USB/external-power arrangement before connecting both. Schematic symbols in the source conflict with the 5 V VIN text; this deck consistently follows the course’s 5 V VIN architecture.')

cards(D,'Extend the Three-Rate Scheduler',[
('MOTION','100 Hz','10 ms interval\nUpdate PWM duty\nand timing metrics.'),
('TELEMETRY','10 Hz','100 ms interval\nRead ADC, filter,\nand report voltage.'),
('HEARTBEAT','1 Hz task','1 second interval\nToggle the LED\non GPIO 4.')],'10, 13–17','Hardware PWM continues at 20 kHz while the loop schedules tasks.')

code('Firmware: Measurement Constants',
'''const uint8_t PIN_BATTERY_ADC = 32;
const float R_TOP = 100000.0f;
const float R_BOTTOM = 22000.0f;
const float DIVIDER_SCALE = (R_TOP + R_BOTTOM) / R_BOTTOM;
const float FILTER_ALPHA = 0.15f;
const float V_BAT_EMPTY = 12.0f, V_BAT_FULL = 16.8f;

float rawV = 0.0f, filteredV = 0.0f, batteryPct = 0.0f;
bool lowBattery = false;''','10–11','Short excerpts use the same values and behavior as the reference firmware.')

code('Firmware: Read and Initialize the ADC',
'''float readBatteryVoltage() {
  return analogReadMilliVolts(PIN_BATTERY_ADC)
         / 1000.0f * DIVIDER_SCALE;
}
void initBatterySensing() {
  pinMode(PIN_BATTERY_ADC, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_BATTERY_ADC, ADC_11db);
  rawV = readBatteryVoltage();
  filteredV = rawV;
}''','11–12','Call initBatterySensing() once in setup(), after the power checks.',ADC_URL)

code('Firmware: Filter and Evaluate',
'''void updateBatterySensing() {
  rawV = readBatteryVoltage();
  filteredV = FILTER_ALPHA * rawV
            + (1.0f - FILTER_ALPHA) * filteredV;
  batteryPct = constrain(
      100.0f * (filteredV - V_BAT_EMPTY)
      / (V_BAT_FULL - V_BAT_EMPTY), 0.0f, 100.0f);
  lowBattery = filteredV < V_BAT_EMPTY;
}''','12–13','Filtering reduces sample variation, but also delays the warning response.')

code('Firmware: Add Sensing at 10 Hz',
'''// Inside loop(); lastTelemetry is initialized in setup().
const uint32_t now = millis();
if (uint32_t(now - lastTelemetry) >= 100) {
  lastTelemetry += 100;
  updateBatterySensing();
  taskTelemetry();
}
// Keep the 100 Hz motion and 1 Hz heartbeat checks separate.''','14–17','Use unsigned elapsed time and advance by the fixed task interval.',extra='In this excerpt, updateBatterySensing() is moved from taskTelemetry() into the scheduling block. Do not call it twice in one telemetry cycle. The full sketch remains in the source PDF.')

code('Firmware: Plot Raw and Filtered Voltage',
'''void taskTelemetry() {
  Serial.printf("V_bat_Raw: %.2f,V_bat_Filt: %.2f\\n",
                rawV, filteredV);
}
// In setup(): Serial.begin(115200);
// Keep text alarms out of this numeric-only plot stream.
// Monitor mode can report batteryPct and lowBattery.''','14–15, 17–18','Plot voltage traces together; a percentage uses a different scale.',extra='Presentation adaptation: numeric-only plotting avoids mixing alarm text and percentage units into the voltage chart. The reference firmware prints additional metrics and alarm text.')

rows(D,'Bench Test: Meter, Monitor, Plotter',[
('Measure','Probe the battery terminals and GPIO 32.\nCompare with the expected voltages on the next slide.'),
('Observe','At 115200 baud, expect 10 samples per second.\nPlot raw and filtered voltage together.'),
('Compare','Aim for agreement within ±0.10 V at the pack\nafter checking divider values and calibration.')],'17–18','Treat ±0.10 V as the lab target, not a guaranteed ADC specification.')

cards(D,'Expected Bench Measurements',[
('FULL PACK','16.80 V','Divider midpoint\n≈ 3.030 V'),
('NOMINAL PACK','14.80 V','Divider midpoint\n≈ 2.669 V'),
('WARNING LEVEL','12.00 V','Divider midpoint\n≈ 2.164 V')],'5, 18','The filtered value should settle near the meter reading.')

rows(D,'Debugging: Wrong Voltage',[
('Reads zero','Check the divider midpoint connection,\nGPIO number, ground path, and resistor joints.'),
('Wrong scale','Verify 100 kΩ / 22 kΩ orientation, measured\nresistor values, and the 5.54545 scale factor.'),
('Clips near full','Check attenuation and the chip input range;\ncompare the physical midpoint voltage first.')],'18','Measure the signal chain in order: pack → divider → ADC → software.')

rows(D,'Debugging: Noise, Lag, and Alarms',[
('Noisy voltage','Inspect motor return routing and connections.\nReduce α if smoothing is insufficient.'),
('Slow tracking','Increase α cautiously from 0.15 toward 0.3;\nconfirm the sampling interval is still 100 ms.'),
('Alarm on startup','Compare raw and filtered sag with a meter\nor scope; check battery and wiring impedance.')],'18–19','Do not hide persistent undervoltage by adding more filtering.')

rows(D,'Lab Completion Checklist',[
('Power verified','5 V logic and 6 V motor rails measured\nwith correct polarity and separate outputs.'),
('Sensing verified','Divider midpoint and reconstructed pack\nvoltage agree with physical measurements.'),
('Software verified','Stable 10 Hz telemetry, primed EMA,\nand the low-voltage condition understood.')],'7, 17–19','Explain each measurement before moving to motor control.')

s=base('>_ KEEP EXPLORING ^_^','References','19')
refs=[('COURSE CONTENT','Power Architecture, Dual Buck Calibration,\nand Analog Battery Sensing — DCLab course PDF',None),
('ADC API','Arduino-ESP32 ADC documentation\nCalibrated readings, resolution, and attenuation',ADC_URL),
('GPIO REFERENCE','ESP32 GPIO & RTC GPIO documentation\nADC1 pins, input-only GPIOs, and Wi-Fi constraints',GPIO_URL),
('FURTHER READING','The Art of Electronics: Student Manual — Hayes & Horowitz\nMaking Embedded Systems — Elecia White',None)]
for i,(label,body,url) in enumerate(refs):
    y=2.25+i*1.02
    t.txt(s,.85,y,2.6,.4,label,13,t.CYAN,font=t.MONO)
    sh=t.txt(s,3.4,y,9.0,.83,body,18)
    if url:
        for para in sh.text_frame.paragraphs:
            for run in para.runs: run.hyperlink.address=url
s.notes_slide.notes_text_frame.text='Primary content: supplied course PDF. Corrections verified using:\n'+ADC_URL+'\n'+GPIO_URL+'\nStyle: the existing MCU/PWM and Embedded Software decks. Reference diagrams redrawn as editable shapes.'

s=clone(0)
for sh in list(s.shapes):
    if 1.0 < sh.top/914400 < 7.0: remove(sh)
t.txt(s,.6,1.5,12,.4,'SESSION 03 / POWER ARCHITECTURE & ADC',13,t.CYAN,font=t.MONO)
t.txt(s,.6,2.35,12,1.0,'Thank you!',48,t.BLUE,True,font=t.MONO)
t.txt(s,.6,3.55,12,.7,'Questions & discussion',28)
# A connected sensing circuit, using battery/resistor/ground symbols and a waveform.
def wire(x1,y1,x2,y2,color=t.CYAN):
    t.line(s,x1,y1,x2,y2,color,1.8)
def resistor(x,y0,y1):
    points=[(x,y0)]+[(x+(.11 if k%2 else -.11),y0+(y1-y0)*k/7) for k in range(1,7)]+[(x,y1)]
    for a,b in zip(points,points[1:]): wire(*a,*b)
wire(2.1,4.55,6.0,4.55)
wire(2.1,4.55,2.1,4.9)
for y,w in [(4.9,.62),(5.06,.32),(5.36,.62),(5.52,.32)]:
    wire(2.1-w/2,y,2.1+w/2,y)
wire(2.1,5.06,2.1,5.36)
wire(2.1,5.52,2.1,6.05)
wire(2.1,6.05,6.0,6.05)
t.txt(s,1.05,4.85,.7,.4,'+',19,t.PINK)
t.txt(s,1.05,5.42,.7,.4,'−',19,t.MUTED)
t.txt(s,2.65,4.71,2.3,.45,'4S battery',16,t.MUTED,font=t.MONO)
wire(6.0,4.55,6.0,4.72)
resistor(6.0,4.72,5.13)
wire(6.0,5.13,6.0,5.46)
resistor(6.0,5.46,5.87)
wire(6.0,5.87,6.0,6.05)
for y,w in [(6.05,.62),(6.14,.4),(6.23,.18)]: wire(6.0-w/2,y,6.0+w/2,y)
t.txt(s,5.0,4.74,.8,.35,'100 kΩ',12,t.MUTED)
t.txt(s,5.0,5.49,.8,.35,'22 kΩ',12,t.MUTED)
t.line(s,6.0,5.3,9.0,5.3,t.CYAN,1.8,True)
t.txt(s,6.55,4.78,2.6,.4,'ADC → EMA',16,t.BLUE,font=t.MONO)
import math as mathlib
raw_points=[]; smooth_points=[]
for i in range(70):
    x=9.35+2.65*i/69
    trend=5.2+.3/(1+mathlib.exp(-(i-26)/5))
    raw_points.append((x,trend+.17*mathlib.sin(i*1.85)))
    smooth_points.append((x,trend))
for points,color in [(raw_points,t.PINK),(smooth_points,t.CYAN)]:
    for a,b in zip(points,points[1:]): t.line(s,*a,*b,color,1.1 if color==t.PINK else 2.2)
wire(9.25,6.05,12.15,6.05,t.RULE)
wire(9.25,4.68,9.25,6.05,t.RULE)
for x,label in [(1.4,'POWER'),(5.25,'SENSE'),(10.0,'FILTER')]:
    t.txt(s,x,6.45,2.4,.32,label,14,t.CYAN,font=t.MONO)

# Expanded teaching sequence: original circuit artwork, focused firmware excerpts,
# typeset mathematics, and the author's exact reference URLs.
initial = list(p.slides)[len(original):]
replacements = {}
insertions = {}
source_md = (ROOT / (NAME + '.md')).read_text()
user_refs = re.findall(r'^- \[(.*?)\]\((.*)\)$', source_md, re.M)
assert len(user_refs) == 8

def title_of(slide):
    for sh in slide.shapes:
        if sh.has_text_frame and abs(sh.top / 914400 - .99) < .03:
            return sh.text
    return ''

def after(title, *slides):
    insertions.setdefault(title, []).extend(slides)

def photo(slide, path, x, y, w, h, crop=None):
    # Native PowerPoint crop: the original image bytes are preserved.
    with Image.open(path) as im:
        iw, ih = im.size
    l, top, r, bottom = crop or (0, 0, 1, 1)
    aspect = iw * (r-l) / (ih * (bottom-top))
    pw, ph = (w, w/aspect) if w/h < aspect else (h*aspect, h)
    pic = slide.shapes.add_picture(str(path), Inches(x+(w-pw)/2),
        Inches(y+(h-ph)/2), width=Inches(pw), height=Inches(ph))
    pic.crop_left, pic.crop_top = l, top
    pic.crop_right, pic.crop_bottom = 1-r, 1-bottom
    pic.name = 'Original course artwork / ' + Path(path).name
    return pic

def math(slide, expression, x, y, w, h, dark=False, size=32):
    # Mathematical typesetting with a high-resolution fallback and vector SVG.
    from pptx.opc.package import Part
    from pptx.opc.packuri import PackURI
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    from pptx.oxml.xmlchemy import OxmlElement
    fig = plt.figure(figsize=(w,h), dpi=300)
    fig.patch.set_alpha(0)
    fig.text(.02,.5,'$'+expression+'$',va='center',ha='left',fontsize=size,
             math_fontfamily='cm', color='#'+(t.PALE if dark else t.BLUE))
    png, svg = io.BytesIO(), io.BytesIO()
    fig.savefig(png,format='png',transparent=True,bbox_inches='tight',pad_inches=.04)
    fig.savefig(svg,format='svg',transparent=True,bbox_inches='tight',pad_inches=.04)
    plt.close(fig); png.seek(0)
    with Image.open(png) as im: iw,ih=im.size
    png.seek(0)
    # Preserve the requested point size; only shrink an equation if it must fit.
    # Stretching every equation to the box height made short lines much too large.
    native_w,native_h=iw/300.0,ih/300.0
    scale=min(1.0,w/native_w,h/native_h)
    pw,ph=native_w*scale,native_h*scale
    sh=slide.shapes.add_picture(png,Inches(x),Inches(y+(h-ph)/2),width=Inches(pw),height=Inches(ph))
    sh.name='Equation / '+expression
    package=slide.part.package
    part=Part(package.next_partname('/ppt/media/equation%d.svg'),'image/svg+xml',package,svg.getvalue())
    rid=slide.part.relate_to(part,RT.IMAGE)
    blip=sh._element.xpath('.//a:blip')[0]
    extlist=OxmlElement('a:extLst'); ext=OxmlElement('a:ext')
    ext.set('uri','{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
    from lxml import etree
    node=etree.SubElement(ext,'{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip')
    node.set(RNS+'embed',rid); extlist.append(ext); blip.append(extlist)
    return sh

def equations(section,title,expressions,pages,takeaway,labels=None):
    slide=base(section,title,pages,takeaway=takeaway)
    for i,expr in enumerate(expressions):
        y=2.25+i*(3.75/len(expressions))
        if labels:
            t.txt(slide,.85,y,2.5,.45,labels[i],15,t.CYAN,font=t.MONO)
            math(slide,expr,3.0,y,9.45,3.5/len(expressions)-.12)
        else:
            math(slide,expr,1.0,y,11.2,3.5/len(expressions)-.12)
    return slide

def schematic(title,filename,pages,notes,crop=None,takeaway=''):
    slide=base(D,title,pages,takeaway=takeaway)
    photo(slide,ROOT/filename,.7,2.18,7.65,3.95,crop)
    for i,(label,body) in enumerate(notes):
        y=2.32+i*1.25
        t.txt(slide,8.7,y,3.9,.35,label,15,t.CYAN,True,font=t.MONO)
        t.txt(slide,8.7,y+.4,3.9,.8,body,17)
    return slide

# Original architecture illustration, then its distribution detail.
s=base(A,'Power Architecture: Original Overview','1',True,
       'The distribution assembly carries separate 5 V and 6 V positive rails.')
photo(s,ROOT/'power_system.excalidraw.png',.7,2.12,8.0,4.05)
t.txt(s,9.05,2.5,3.5,.4,'FOLLOW THE POWER',15,'48CAE4',font=t.MONO)
t.txt(s,9.05,3.15,3.5,2.7,'Battery → fuse → bus\n\nTwo buck branches\n\nLogic and motor loads',21,t.PALE)
replacements['Separate Rails, Common Ground']=[s]
s=rows(A,'Trace Each Power Rail',[
('Battery bus','The fused battery positive feeds both buck\ninputs; raw battery voltage is 12–16.8 V.'),
('5 V logic rail','Buck 1 supplies ESP32 VIN and suitable\n5 V loads. It does not connect to the 3V3 pin.'),
('6 V motor rail','Buck 2 supplies driver VM in this course\nexample; check the actual motor voltage rating.')],
'1–2','Keep the two positive outputs separate; connect their returns to the ground bus.')
after('Separate Rails, Common Ground',s)

after('One Battery, Two Different Loads',rows(A,'Why Motor Startup Can Reset the MCU',[
('Current step','Starting or stalling a motor increases current\nthrough the battery and shared wiring.'),
('Voltage drop','Battery resistance and connection impedance\nturn that current step into supply voltage sag.'),
('Logic consequence','If the MCU supply drops too far, operation\nbecomes unreliable and a reset may occur.')],'1–2','Two regulators reduce coupling; they do not remove shared-path impedance.'))

after('The 4S Battery Operating Range',equations(A,'Four Cells in Series: Voltage Adds',[
 r'V_{\mathrm{pack}}=V_1+V_2+V_3+V_4',
 r'V_{\mathrm{full}}=4\times4.2\,\mathrm{V}=16.8\,\mathrm{V}',
 r'V_{\mathrm{nom}}=4\times3.7\,\mathrm{V}=14.8\,\mathrm{V}'
],'2','4S1P means four cells in series and one parallel string.'))
replacements['Buck Regulator Input Headroom']=[equations(A,'Buck Regulator Input Headroom',[
 r'V_{\mathrm{in,min}}\geq V_{\mathrm{out}}+V_{\mathrm{dropout}}',
 r'V_{\mathrm{in,min}}\geq6.0\,\mathrm{V}+1.5\,\mathrm{V}=7.5\,\mathrm{V}',
 r'12.0\,\mathrm{V}-7.5\,\mathrm{V}=4.5\,\mathrm{V}'
],'2','This is the course headroom example; verify the actual module under load.')]

after('Protection and Return Paths',rows(A,'Fuse and Star Bus: Physical Placement',[
('Battery positive','Place the reference 2 A fuse near the battery\nbefore the main positive distribution terminal.'),
('Battery negative','Use the main negative terminal as the\ncommon reference for the return branches.'),
('Motor return','Run suitable heavy wire from the drivers\nto the bus; do not pass it through logic wiring.')],'2–3','Reference wiring uses AWG 18 for the main feed and AWG 18–20 for returns.'))

# Expand calibration into actual measurement steps.
replacements['Calibrate the Two Buck Outputs']=[
rows(B,'Measure the Battery Before Adjustment',[
('Meter mode','Select DC voltage; use a range above the\nmaximum pack voltage of 16.8 V.'),
('Probe placement','Black probe → main negative terminal.\nRed probe → fused battery-positive bus.'),
('Cross-check','Read the meter and the battery display.\nThe course comparison target is ±0.10 V.')],'7','Confirm a positive reading and correct polarity before adjusting either buck.'),
rows(B,'Calibrate Buck 1: The 5 V Logic Rail',[
('Disconnect loads','Leave ESP32 VIN and the logic loads\ndisconnected during initial adjustment.'),
('Measure output','Probe OUT+ relative to OUT− on Buck 1.\nKeep the probes clear of neighboring terminals.'),
('Adjust + compare','Turn the trimmer while watching the meter.\nSet 5.00 V and compare the 5 V display.')],'7','Use the meter as the reference; trimmer direction depends on the module.'),
rows(B,'Calibrate Buck 2: The 6 V Motor Rail',[
('Disconnect drivers','Keep motor-driver VM disconnected\nwhile setting the output voltage.'),
('Measure output','Probe Buck 2 OUT+ relative to OUT−.\nAdjust carefully until the meter reads 6.00 V.'),
('Label + verify','Compare the motor-rail display and label\nthe output before reconnecting the driver.')],'7','After reconnecting, check the output during startup and normal motor loading.')]

# Use the supplied resistor schematic with the mathematical derivation beside it.
s=base(C,'Resistive Divider: Circuit and Equation','3–5, 8',takeaway='Use top/bottom names in the calculations; the schematic labels these R2 and R3.')
photo(s,ROOT/'core.PNG',.85,2.2,3.1,3.9,(.682,0,1,1))
math(s,r'V_{\mathrm{pin}}=V_{\mathrm{bat}}\frac{R_{\mathrm{bottom}}}{R_{\mathrm{top}}+R_{\mathrm{bottom}}}',4.45,2.45,8.0,1.15)
math(s,r'R_{\mathrm{top}}=100\,\mathrm{k}\Omega,\quad R_{\mathrm{bottom}}=22\,\mathrm{k}\Omega',4.45,3.9,8.0,.8,size=26)
t.txt(s,4.45,5.0,7.9,.95,'VDIV is the midpoint connected to GPIO 32.\nR2 is above VDIV; R3 is below it.',20)
replacements['Scale the Battery Voltage Safely']=[s]
after('Scale the Battery Voltage Safely',equations(C,'Calculate the Divider Ratio',[
 r'K_{\mathrm{div}}=\frac{R_{\mathrm{bottom}}}{R_{\mathrm{top}}+R_{\mathrm{bottom}}}',
 r'K_{\mathrm{div}}=\frac{22\,\mathrm{k}\Omega}{100\,\mathrm{k}\Omega+22\,\mathrm{k}\Omega}',
 r'K_{\mathrm{div}}=\frac{22}{122}\approx0.1803279'
],'4–5','The ADC receives about 18.03% of the battery voltage.'))
replacements['Check the Divider at Both Limits']=[equations(C,'Check the Divider at Both Limits',[
 r'V_{\mathrm{pin,max}}=16.8\,\mathrm{V}\times\frac{22}{122}\approx3.0295\,\mathrm{V}',
 r'V_{\mathrm{pin,min}}=12.0\,\mathrm{V}\times\frac{22}{122}\approx2.1639\,\mathrm{V}'
],'5','Measure the assembled midpoint before connecting it to the ADC.')]
after('Check the Divider at Both Limits',equations(C,'Divider Current and ADC Headroom',[
 r'I_{\mathrm{div}}=\frac{V_{\mathrm{bat}}}{R_{\mathrm{top}}+R_{\mathrm{bottom}}}=\frac{16.8\,\mathrm{V}}{122\,\mathrm{k}\Omega}\approx137.7\,\mu\mathrm{A}',
 r'3.10\,\mathrm{V}-3.0295\,\mathrm{V}=70.5\,\mathrm{mV}',
 r'V_{\mathrm{pin,max,1\%}}=16.8\,\mathrm{V}\frac{22.22}{99+22.22}\approx3.0795\,\mathrm{V}'
],'5','1% tolerance example: top −1%, bottom +1%. Check the actual ADC input range.'))

after('ADC Resolution and Input Range',equations(C,'Quantization: The Ideal 3.3 V Model',[
 r'2^{12}=4096\ \mathrm{levels},\qquad N_{\mathrm{ADC}}\in\{0,\ldots,4095\}',
 r'q_{\mathrm{pin}}=\frac{3.3\,\mathrm{V}}{4096}\approx0.80566\,\mathrm{mV/count}',
 r'q_{\mathrm{battery}}=q_{\mathrm{pin}}\frac{122}{22}\approx4.4678\,\mathrm{mV/count}'
],'5–6','An ideal 12-bit quantizer has 4096 bins; this is not an ESP32 calibration model.'))
replacements['Reconstruct the Battery Voltage']=[equations(C,'Undo the Divider: Reconstruct Voltage',[
 r'K_{\mathrm{inv}}=\frac{R_{\mathrm{top}}+R_{\mathrm{bottom}}}{R_{\mathrm{bottom}}}=\frac{122}{22}\approx5.54545',
 r'V_{\mathrm{pin}}=2669\,\mathrm{mV}=2.669\,\mathrm{V}',
 r'V_{\mathrm{bat}}=V_{\mathrm{pin}}K_{\mathrm{inv}}=2.669\,\mathrm{V}\times\frac{122}{22}\approx14.80\,\mathrm{V}'
],'6, 11–12','Firmware reads calibrated millivolts, then applies the external divider ratio.')]
after('Reconstruct the Battery Voltage',equations(C,'Raw Counts: The Course Endpoint Approximation',[
 r'V_{\mathrm{pin}}\approx\frac{N_{\mathrm{ADC}}}{4095}\times3.3\,\mathrm{V}',
 r'V_{\mathrm{bat}}\approx\frac{N_{\mathrm{ADC}}}{4095}\times3.3\,\mathrm{V}\times\frac{122}{22}',
 r'V_{\mathrm{bat}}\approx N_{\mathrm{ADC}}\times0.0044689\,\mathrm{V}'
],'6','Dividing by 4095 maps both endpoints; it differs from the 4096-bin quantization step.'))

replacements['Exponential Moving Average (EMA)']=[equations(C,'Exponential Moving Average (EMA)',[
 r'y[k]=\alpha x[k]+(1-\alpha)y[k-1]',
 r'\alpha=0.15\quad\Rightarrow\quad y[k]=0.15x[k]+0.85y[k-1]'
],'6–7, 12','x[k]: new sample; y[k − 1]: previous result; y[k]: updated result.')]
after('Exponential Moving Average (EMA)',equations(C,'Work Through One Filter Update',[
 r'x[k]=14.2\,\mathrm{V},\qquad y[k-1]=14.8\,\mathrm{V}',
 r'y[k]=0.15(14.2\,\mathrm{V})+0.85(14.8\,\mathrm{V})',
 r'y[k]=2.13\,\mathrm{V}+12.58\,\mathrm{V}=14.71\,\mathrm{V}'
],'6–7, 12','Worked example: one low sample moves the filtered value by only 0.09 V.'))

# A scientific plot illustrates the same EMA equation; values are illustrative.
s=base(C,'See the Effect of the Filter','6–7',takeaway='Illustrative 10 Hz samples: smoothing reduces variation but adds response lag.')
import numpy as np
times=np.arange(60)/10
raw=np.where(times<2,14.8,14.2)+.12*np.sin(np.arange(60)*2.1)
filtered=[raw[0]]
for value in raw[1:]: filtered.append(.15*value+.85*filtered[-1])
fig,ax=plt.subplots(figsize=(10.9,3.55),dpi=220)
fig.patch.set_facecolor('#'+t.BG);ax.set_facecolor('#'+t.BG)
ax.plot(times,raw,color='#'+t.PINK,lw=1.5,label='Raw sample')
ax.plot(times,filtered,color='#'+t.CYAN,lw=2.7,label=r'EMA ($\alpha=0.15$)')
ax.set(xlabel='Time (s)',ylabel='Battery voltage (V)',ylim=(13.95,15.05))
ax.grid(alpha=.2);ax.legend(loc='upper right');fig.tight_layout()
buf=io.BytesIO();fig.savefig(buf,format='png');plt.close(fig);buf.seek(0)
s.shapes.add_picture(buf,Inches(.95),Inches(2.2),width=Inches(11.4),height=Inches(3.85))
after('Choose the Smoothing Coefficient',s)
replacements['Battery Percentage and Low Voltage']=[equations(C,'Battery Percentage and Low Voltage',[
 r'P=\operatorname{clamp}\left(100\frac{V_{\mathrm{filtered}}-12.0\,\mathrm{V}}{16.8\,\mathrm{V}-12.0\,\mathrm{V}},\ 0,\ 100\right)\%',
 r'V_{\mathrm{filtered}}<12.0\,\mathrm{V}\quad\Rightarrow\quad\mathrm{low\ battery\ warning}'
],'12–15','This is a voltage indicator, not true state of charge; the code reports a warning.')]

# Full schematic rendering preserves the supplied drawing and net labels.
asset_dir=Path(tempfile.mkdtemp(prefix='power-slide-assets-'))
subprocess.run(['pdftoppm','-scale-to','3000','-singlefile','-png',
    str(ROOT/'power_system_circuit.pdf'),str(asset_dir/'circuit')],check=True)
s=base(D,'Power System: Full Reference Schematic','8–9',takeaway='Read VBAT, VM, VDIV, LED, and GNDREF as connected nets across the sheet.')
photo(s,asset_dir/'circuit.png',.65,2.15,12.05,3.55,(.096,.257,.811,.582))
t.txt(s,.85,5.88,11.8,.37,'Original 3.3 V / 12 V drawing; the lab uses 5 V → VIN and a separate motor rail.',16,t.PINK)
details=[s]
details.append(schematic('Schematic: Battery, Fuse, and Buck Supplies','buck.PNG','9',[
('VBAT + F1','Battery feed through\nthe 2 A reference fuse.'),
('U2 / U3','Both converter branches\nshare GNDREF.'),
('READ THE LABELS','Drawing: 3.3 V / 12 V.\nLab procedure: 5 V / 6 V.')],takeaway='Use adjustable modules for the lab setpoints; the original labels are shown unchanged.'))
details.append(schematic('Schematic: ESP32 and Battery Sensing','core.PNG','8',[
('R2 / R3','100 kΩ above VDIV;\n22 kΩ below VDIV.'),
('VDIV → D32','The divider midpoint\nfeeds GPIO 32 / ADC1.'),
('LAB POWER INPUT','Connect the 5 V rail\nto VIN, not to 3V3.')],takeaway='The shown 3V3 connection belongs to the drawing’s 3.3 V supply version.'))
details.append(schematic('Schematic: PWM LED and Current Limiting','divider.PNG','9',[
('LED NET','The core drawing maps\nthis net to GPIO 18.'),
('R1 = 330 Ω','Series resistor limits\ncurrent through D1.'),
('D1 → GNDREF','Confirm LED polarity\nand the return path.')],takeaway='This supplied image shows the PWM LED circuit; the heartbeat uses GPIO 4.'))
after('Connect the Measurement Chain',*details)

# Key additions for this lesson; shared PWM/heartbeat scaffolding stays in the PDF.
key_code=[
('Configure the Battery Measurement','10',
'''const uint8_t PIN_BATTERY_ADC = 32;
const float R_TOP_OHMS = 100000.0f;
const float R_BOTTOM_OHMS = 22000.0f;
const float DIVIDER_SCALE =
  (R_TOP_OHMS + R_BOTTOM_OHMS) / R_BOTTOM_OHMS;
const float FILTER_ALPHA = 0.15f;
const float V_BAT_EMPTY = 12.0f;''',
'Keep the pin, divider scale, filter coefficient, and warning threshold together.'),
('Read Calibrated Battery Voltage','11–12',
'''float readBatteryVoltage() {
  const uint32_t pin_voltage_millivolts =
    analogReadMilliVolts(PIN_BATTERY_ADC);
  const float pin_voltage =
    pin_voltage_millivolts / 1000.0f;
  return pin_voltage * DIVIDER_SCALE;
}''',
'Convert calibrated millivolts to volts, then undo the resistor divider.'),
('Initialize the ADC and Prime the Filter','12',
'''void initBatterySensing() {
  pinMode(PIN_BATTERY_ADC, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_BATTERY_ADC, ADC_11db);

  raw_battery_voltage = readBatteryVoltage();
  filtered_battery_voltage = raw_battery_voltage;
}''',
'Call once in setup(); initialize the filtered state from a real sample.'),
('Filter and Check the Battery','12–13',
'''void updateBatterySensing() {
  raw_battery_voltage = readBatteryVoltage();
  filtered_battery_voltage =
    FILTER_ALPHA * raw_battery_voltage +
    (1.0f - FILTER_ALPHA) * filtered_battery_voltage;
  low_battery_flag =
    filtered_battery_voltage < V_BAT_EMPTY;
}''',
'Update the EMA and evaluate the warning against the filtered voltage.'),
('Report the Two Voltage Traces','14',
'''void taskTelemetry() {
  updateBatterySensing();
  Serial.printf(
    "V_bat_Raw: %.2f,V_bat_Filt: %.2f\\n",
    raw_battery_voltage, filtered_battery_voltage);
}''',
'Focused plot output: compare the raw and filtered voltage at 10 Hz.'),
('Report the Low-Battery Condition','14–15',
'''if (low_battery_flag) {
  Serial.println(
    "[ALARM] LOW BATTERY VOLTAGE BELOW 12.0 V"
  );
}''',
'Add inside the telemetry task for Serial Monitor use; omit text alarms while plotting.'),
('Schedule Battery Sensing at 10 Hz','17',
'''if ((uint32_t)(current_time_ms - last_telemetry_time_ms)
    >= INTERVAL_TELEMETRY_MS) {

  last_telemetry_time_ms += INTERVAL_TELEMETRY_MS;
  taskTelemetry();
}''',
'Inside loop(): a 100 ms interval, independent of motion and heartbeat timing.')]
focused_code=[]
for i,(title,pages,snippet,takeaway) in enumerate(key_code,1):
    slide=base(f'04 / Implementation / Key Firmware {i:02} of {len(key_code):02}',
               title,pages,True,takeaway)
    # Larger type, generous padding, and a 1.45-line baseline rhythm.
    sh=t.codebox(slide,.7,2.22,11.95,3.91,snippet,size=21)
    sh.text_frame.margin_left=sh.text_frame.margin_right=Inches(.32)
    sh.text_frame.margin_top=sh.text_frame.margin_bottom=Inches(.23)
    for para in sh.text_frame.paragraphs:
        para.line_spacing=Pt(21*1.45)
    slide.notes_slide.notes_text_frame.text=(
      f'Focused teaching excerpt from the course PDF, pages {pages}. '
      'Uses the original identifiers; complete declarations, PWM, heartbeat, '
      'percentage calculation, and setup scaffolding are in the source PDF. '
      'Telemetry is reduced to the two voltage traces for plotting. '
      'The low-battery reporting snippet belongs inside the telemetry task in monitor mode.\n'+snippet)
    focused_code.append(slide)
old_code=[title_of(slide) for slide in initial if title_of(slide).startswith('Firmware:')]
for title in old_code: replacements[title]=[]
replacements[old_code[0]]=focused_code

# Use all eight of the user's exact URLs, including the original book links.
ref_slides=[]
for j,group in enumerate([user_refs[:4],user_refs[4:]],1):
    slide=base('>_ KEEP EXPLORING ^_^',f'References / {j} of 2','19')
    for i,(label,url) in enumerate(group):
        label=[
          'The Art of Electronics: Student Manual\nThomas C. Hayes and Paul Horowitz',
          'Making Embedded Systems: Design Patterns for Great Software\nElecia White',
          'Feedback Systems: An Introduction for Scientists and Engineers\nKarl Johan Åström and Richard M. Murray',
          'ADC Peripheral API Documentation — Espressif Systems',
          'GPIO Peripheral API Documentation — Espressif Systems',
          'Espressif Centralized Documentation Platform (CDP)',
          'Arduino Core for ESP32 Documentation — Espressif Systems',
          'Arduino Language Reference — Arduino'][(j-1)*4+i]
        y=2.22+i*1.04
        number=t.txt(slide,.85,y,.6,.5,f'{(j-1)*4+i+1:02}',23,t.PINK,font=t.MONO)
        # The entire title, not just a bare URL, is a clickable hyperlink.
        sh=t.txt(slide,1.7,y,10.65,.85,label,20,t.BLUE)
        for para in sh.text_frame.paragraphs:
            for run in para.runs:
                run.hyperlink.address=url
                run.font.underline=True
        t.line(slide,1.7,y+.92,12.55,y+.92)
    slide.notes_slide.notes_text_frame.text='Exact links supplied in the course notes:\n'+'\n'.join(url for _,url in group)
    ref_slides.append(slide)
replacements['References']=ref_slides

# Reorder by lesson topic, discard replaced slides, and retain reusable layouts.
ordered=[]
for slide in initial:
    title=title_of(slide)
    ordered.extend(replacements.get(title,[slide]))
    ordered.extend(insertions.get(title,[]))
ids={slide.slide_id: sid for slide,sid in zip(p.slides,list(p.slides._sldIdLst))}
keep={slide.slide_id for slide in ordered}
ordered_ids=[ids[slide.slide_id] for slide in ordered]
for sid in list(p.slides._sldIdLst):
    if int(sid.id) not in keep: p.part.drop_rel(sid.rId)
    p.slides._sldIdLst.remove(sid)
for sid in ordered_ids: p.slides._sldIdLst.append(sid)
for i,slide in enumerate(p.slides,1):
    dark=slide.background.fill.fore_color.rgb==t.rgb(t.NAVY)
    t.txt(slide,12.2,7.14,.5,.19,f'{i:02}',9,'828BB8' if dark else t.MUTED,font=t.MONO)
p.core_properties.title=NAME
p.core_properties.subject='DCLab Control System Crash Course / Session 03'
p.core_properties.author='DCLab'
p.core_properties.keywords='power architecture, buck calibration, ESP32, ADC, battery sensing'
p.save(ROOT / (NAME+'.pptx'))
print(f'Saved {len(p.slides)} slides: {ROOT / (NAME+".pptx")}')
