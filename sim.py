class Powerwall:
    MAX_CHARGE = 13.5 * 3600
    MAX_TRANSFER_RATE = 5


class SimulationType:
    COMPLETE = 'COMPLETE'
    RELAXED = 'RELAXED'
    APPROXIMATE = 'APPROXIMATE'


class Simulation:
    """
        charge_inputs = u_c
        discharge_inputs = u_d
        initial_charge = x_0
        timestep_duration = delta_t
        max_charge = E
        max_transfer_rate = P
        charge_efficiency = n_c
        discharge_efficiency = n_d
    """
    def __init__(self, name, charge_inputs, discharge_inputs, initial_charge, timestep_duration,
                 max_charge, max_transfer_rate, charge_efficiency, discharge_efficiency):
        self.name = name
        self.charge_inputs = charge_inputs
        self.discharge_inputs = discharge_inputs
        self.initial_charge = initial_charge
        self.timestep_duration = timestep_duration
        self.max_charge = max_charge
        self.max_transfer_rate = max_transfer_rate
        self.charge_efficiency = charge_efficiency
        self.discharge_efficiency = discharge_efficiency

    """
    Advance the simulation a single timestep. Based on the simulation type, use the
    appropriate formula to calculate the next value for the state of charge.
    """
    def take_timestep(self, timestep, state_of_charge, simulation_type):
        charge_input = self.charge_inputs[timestep]
        discharge_input = self.discharge_inputs[timestep]

        if simulation_type == SimulationType.COMPLETE:
            net_charging_input = charge_input - discharge_input
            if net_charging_input > 0:
                return state_of_charge + (self.timestep_duration * net_charging_input
                                          * self.charge_efficiency)

            return state_of_charge - (self.timestep_duration * -net_charging_input
                                      / self.discharge_efficiency)

        if simulation_type == SimulationType.RELAXED:
            return state_of_charge + (self.timestep_duration *
                                      ((charge_input * self.charge_efficiency)
                                       - (discharge_input / self.discharge_efficiency)))

        return state_of_charge + (self.timestep_duration * (charge_input - discharge_input))

    """
    Run the simulation in its entirety.
    """
    def simulate(self, simulation_type):

        assert len(self.charge_inputs) == len(self.discharge_inputs)
        timesteps = len(self.charge_inputs)

        outputs = [self.initial_charge]
        state_of_charge = self.initial_charge

        for timestep in range(0, timesteps):
            state_of_charge = max(min(self.take_timestep(timestep, state_of_charge, simulation_type), self.max_charge), 0)
            outputs.append(state_of_charge)

        return outputs


def complementarity_holds():
    charge_inputs = []
    discharge_inputs = []
    for i in range(0, 3600 * 8):
        charge_inputs.append(0)
        discharge_inputs.append(1)
    for i in range(0, 3600 * 8):
        charge_inputs.append(0.5)
        discharge_inputs.append(0)
    for i in range(0, 3600 * 8):
        charge_inputs.append(0)
        discharge_inputs.append(1)

    yield Simulation(
        'Complementarity, n_c = n_d = 1',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=1,
        charge_efficiency=1,
    )

    yield Simulation(
        'Complementarity, n_c = n_d = 0.95',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.95,
        charge_efficiency=.95,
    )

    yield Simulation(
        'Complementarity, n_c = 0.8, n_d = 0.9',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.9,
        charge_efficiency=.8,
    )


def complementarity_does_not_hold():
    charge_inputs = []
    discharge_inputs = []
    for i in range(0, 3600 * 8):
        charge_inputs.append(0)
        discharge_inputs.append(1)
    for i in range(0, 3600 * 8):
        charge_inputs.append(1.5)
        discharge_inputs.append(1)
    for i in range(0, 3600 * 8):
        charge_inputs.append(0.5)
        discharge_inputs.append(1)

    yield Simulation(
        'No complementarity, n_c = n_d = 1',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=1,
        charge_efficiency=1,
    )

    yield Simulation(
        'No complementarity, n_c = n_d = 0.95',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.95,
        charge_efficiency=.95,
    )

    # yield Simulation(
    #     'No complementarity, n_c = 0.8, n_d = 0.9',
    #     charge_inputs=charge_inputs,
    #     discharge_inputs=discharge_inputs,
    #     initial_charge=Powerwall.MAX_CHARGE,
    #     timestep_duration=1,
    #     max_charge=Powerwall.MAX_CHARGE,
    #     max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
    #     discharge_efficiency=.9,
    #     charge_efficiency=.8,
    # )


def bad_divergence():
    charge_inputs = []
    discharge_inputs = []
    for i in range(0, 3600 * 8):
        charge_inputs.append(1.5)
        discharge_inputs.append(1)

    yield Simulation(
        'No complementarity, n_c = 0.9, n_d = 0.3',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE / 2,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.3,
        charge_efficiency=.9,
    )


def prompt_4_counterexample():
    charge_inputs = []
    discharge_inputs = []
    for i in range(0, 3600 * 8):
        charge_inputs.append(1.5)
        discharge_inputs.append(1)

    yield Simulation(
        'Prompt 4 counterexample, n_d = .8, n_c = .9',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE / 2,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.8,
        charge_efficiency=.9,
    )


def prompt_5_counterexample():
    charge_inputs = []
    discharge_inputs = []
    for i in range(0, 3600 * 8):
        charge_inputs.append(0.5)
        discharge_inputs.append(1)

    yield Simulation(
        'Prompt 5 counterexample, n_d = .2',
        charge_inputs=charge_inputs,
        discharge_inputs=discharge_inputs,
        initial_charge=Powerwall.MAX_CHARGE / 2,
        timestep_duration=1,
        max_charge=Powerwall.MAX_CHARGE,
        max_transfer_rate=Powerwall.MAX_TRANSFER_RATE,
        discharge_efficiency=.2,
        charge_efficiency=1,
    )


def build_simulations():
    #yield from complementarity_holds()
    #yield from complementarity_does_not_hold()
    yield from bad_divergence()
    #yield from prompt_4_counterexample()
    #yield from prompt_5_counterexample()
