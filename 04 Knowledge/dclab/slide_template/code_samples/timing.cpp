// One quick task; then return to the loop.
constexpr uint32_t PERIOD_MS = 10;
uint32_t previous = 0;

void loop() {
  const uint32_t now = millis();
  if (uint32_t(now - previous) >= PERIOD_MS) {
    previous = now;
    read_sensor();
  }
  poll_serial();
}
