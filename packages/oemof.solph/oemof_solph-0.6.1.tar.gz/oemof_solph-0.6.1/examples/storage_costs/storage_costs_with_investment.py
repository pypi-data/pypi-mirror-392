import pandas as pd

from oemof import solph


def main(optimize=True):
    idx = pd.date_range("1/1/2023", periods=12, freq="h")
    es = solph.EnergySystem(timeindex=idx, infer_last_interval=False)

    bel = solph.Bus(label="bel")
    es.add(bel)

    fixed_size = False
    if fixed_size:
        storage_capacity = 10
    else:
        storage_capacity = solph.Investment(ep_costs=0, minimum=10, maximum=10)

    battery = solph.components.GenericStorage(
        label="battery",
        nominal_capacity=storage_capacity,
        inputs={
            bel: solph.Flow(
                nominal_capacity=1,
            )
        },
        outputs={
            bel: solph.Flow(
                nominal_capacity=1,
            )
        },
        storage_costs=1,
        initial_storage_level=0.5,
    )
    es.add(battery)

    if optimize is False:
        return es

    model = solph.Model(es)

    model.solve(solver="cbc", solve_kwargs={"tee": False})

    print("Objective value: ", model.objective())

    results = solph.processing.results(model)
    print(results[(battery, None)]["sequences"])


if __name__ == "__main__":
    main()
