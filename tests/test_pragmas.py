from slurm_script_generator.pragmas import PragmaFactory


def test_pragma_factory():
    pragma = PragmaFactory.create_pragma("nodes", 2)
    assert pragma.flags == ["-N", "--nodes"]
    assert pragma.dest == "--nodes"
    assert pragma.type is int
    assert pragma.value == 2


def test_pragma_var_names():
    pragmas = PragmaFactory.pragmas
    for key, pragma_cls in pragmas.items():
        assert pragma_cls.arg_varname == key, (
            f"Pragma arg_varname '{pragma_cls.arg_varname}' "
            + f"does not match key '{key}'"
        )
        assert pragma_cls.arg_varname == pragma_cls.__name__.lower(), (
            f"Pragma arg_varname '{pragma_cls.arg_varname}' "
            + f"does not match class name '{pragma_cls.__name__}'"
        )


def test_pragma_serialization():
    pragma = PragmaFactory.create_pragma("nodes", 3)
    d = pragma.to_dict()
    assert isinstance(d, dict)
    assert list(d.keys())[0] == "nodes"
    assert list(d.values())[0] == 3
    # Re-create from dict
    key, value = list(d.items())[0]
    pragma2 = PragmaFactory.create_pragma(key, value)
    assert pragma2.value == 3
    assert pragma2.dest == "--nodes"


def test_invalid_pragma_key():
    import pytest

    with pytest.raises(ValueError):
        PragmaFactory.create_pragma("notarealpragma", "1")


def test_all_pragmas_have_flags_and_dest():
    for _, pragma_cls in PragmaFactory.pragmas.items():
        pragma = pragma_cls("test")
        assert hasattr(pragma, "flags")
        assert hasattr(pragma, "dest")
        assert isinstance(pragma.flags, list)
        assert isinstance(pragma.dest, str)


def test_pragma_type_and_value():
    pragma = PragmaFactory.create_pragma("nodes", 4)
    assert pragma.type is int
    assert isinstance(pragma.value, int)
    pragma = PragmaFactory.create_pragma("account", "max")
    assert pragma.type is str
    assert isinstance(pragma.value, str)


def test_import_all_pragmas():
    from slurm_script_generator.pragmas import (  # --- Time & Priority ---; --- Standard IO & Directory ---; --- Notifications ---; --- Dependencies & Job Arrays ---; --- Core Node & Task Allocation ---; --- CPU Topology & Binding ---; --- Memory ---; --- GPUs ---; --- Generic Resources (GRES/TRES) & Licenses ---; --- Node Constraints & Specific Selection ---; --- Exclusivity & Sharing ---; --- Execution Behavior & Signals ---; --- Advanced / Hardware / Misc ---; --- Plugins (Burst Buffer & Containers) ---
        Account, Array, Bb_file, Begin, Bell, Burst_buffer, Chdir,
        Cluster_constraint, Clusters, Comment, Constraint, Container,
        Container_id, Contiguous, Core_spec, Cores_per_socket, Cpu_freq,
        Cpus_per_gpu, Cpus_per_task, Deadline, Delay_boot, Dependency,
        Disable_stdout_job_summary, Distribution, Exclude, Exclusive_mcs,
        Exclusive_user, Extra_node_info, Get_user_env, Gpu_bind, Gpu_freq,
        Gpus, Gpus_per_node, Gpus_per_socket, Gpus_per_task, Gres, Gres_flags,
        Hint, Hold, Immediate, Job_name, Kill_command, Licenses, Mail_type,
        Mail_user, Mcs_label, Mem, Mem_bind, Mem_per_cpu, Mem_per_gpu, Mincpus,
        Nice, No_kill, Nodefile, Nodelist, Nodes, Ntasks, Ntasks_per_core,
        Ntasks_per_node, Ntasks_per_socket, Nvmps, Oom_kill_step, Overcommit,
        Oversubscribe, Partition, Power, Priority, Profile, Qos, Quiet, Reboot,
        Reservation, Resv_ports, Signal, Sockets_per_node, Spread_job, Stderr,
        Stdout, Switches, Thread_spec, Threads_per_core, Time, Time_min, Tmp,
        Tres_bind, Tres_per_task, Use_min_nodes, Wckey)

    for key, pragma_cls in PragmaFactory.pragmas.items():
        pragma = PragmaFactory.create_pragma(key, "testvalue")
        assert pragma.value == "testvalue"
