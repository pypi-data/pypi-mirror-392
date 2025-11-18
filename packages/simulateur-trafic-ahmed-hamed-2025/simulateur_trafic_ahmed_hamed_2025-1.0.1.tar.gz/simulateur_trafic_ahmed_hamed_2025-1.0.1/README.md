
 

# Simulateur de Trafic (Traffic Simulator)

**Simulateur de Trafic** is a Python package for simulating vehicle traffic on customizable road networks.
It models vehicle motion, road connections, and collects useful traffic statistics for analysis and optimization.

 

## Features

* Vehicle movement simulation on a configurable road network
* Roads with speed limits and lengths
* Traffic statistics (speed, flow, time)
* Results exportable to CSV or JSON
* Fully customizable through a JSON configuration file
 
 

## Installation

### From PyPI

```bash
pip install simulateur-trafic-ahmed-hamed-2025
```

### For development (editable mode)

```bash
pip install -e .
```

---

## Usage

### Default execution

```bash
simulateur-trafic
```

Runs the simulation with:

* `n_tours=5`
* `delta_t=60` (seconds)
* `config=config_reseau.json`

---

### Custom parameters

You can specify the number of simulation turns, time step, and configuration file path:

```bash
simulateur-trafic --n_tours 10 --delta_t 30 --config config_reseau.json
```

Or run it directly from Python:

```bash
python -m simulateur_trafic.main --n_tours 10 --delta_t 30 --config config_reseau.json
```

---

## License

This project is licensed under the **MIT License**.
See the `LICENSE` file for details.

---

## Author

**Ahmed Hamed**
📧 [ahmad.hamed.work@gmail.com](mailto:ahmad.hamed.work@gmail.com)

---

 
