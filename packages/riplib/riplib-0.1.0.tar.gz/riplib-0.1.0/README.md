howdy. ts the new 'lib.

## >> riplib
riplib is designed to cover ALL of your bursting, souping and farting needs.

### EXAMPLES

```python
from riplib.ass import AssClient
from riplib.types import Smell, Power, Persistence

# Initialize the booty 
client = AssClient()

# Define a listener using the on_rip decorator
@client.on_rip
def handle_rip_event(fart):
    print(f"Fart detected! Smell: {fart.smell}, Power: {fart.power}, Persistence: {fart.persistence}")

# Generate some farts
client.rip(smell=Smell.PUTRID, power=Power.EXPLOSIVE, persistence=Persistence.ETERNAL)
client.rip() # random values
```

```python
from riplib.models import Fart
from riplib.types import Smell, Power, Persistence

fart = Fart(Smell.PUTRID, Power.EXPLOSIVE, Persistence.ETERNAL)
print(f"Is burst: {fart.is_burst()}")
```

### CONTRIBUTING

Feel like adding your own flavor to 'lib. all contributions welcome. our team will be thoroughly reviewing them before merging.

And a MASSIVE thanks to our contributors & sponsors.

### BUILDING

To build run:

```bash
python setup.py sdist bdist_wheel
```

This will generate the distribution files in the `dist/` directory.

### FOOTER

made with soup by the self.rip() team.

