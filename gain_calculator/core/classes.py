"""
Module containing the core classes of the GainCalculator project. End user should not be concerned about this.
A convention is used that principal quantum number is denoted n and orbital quantum number is denoted l, keep
this in mind.
"""
import re
import fac_helpers


class LevelTerm:
    """
    Simple comparable data class representing a term of form 2p+(1)1
    where the last number is 2*J (J = total angular momentum over all shells).
    The rest of the shell notation is documented elsewhere.

    :ivar shell: shell object instance
    :ivar j2: double the value of total angular momentum
    """

    def __init__(self, shell, j2):  # type: (Shell, int) -> None
        """
        Init using a shell and total angular momentum
        :param shell: shell object instance
        :param j2: double the value of total angular momentum
        """
        self.shell = shell
        self.j2 = j2
        assert j2 >= 0, "Total angular momentum (J2) in {} is negative".format(self)

    def __repr__(self):  # type: () -> str
        return str(self.shell) + str(self.j2)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):  # type: (LevelTerm, LevelTerm) -> bool
        return not self == other


class Shell:
    """
    Class representing a single shell of form 3d+4(2), where 3 is the principal quantum number
    d is the orbital quantum number (2) + represents spin direction (up),
    4 is electron count and 2 is double the value of angular momentum of the shell.

    :ivar n: Starting from 1
    :ivar l: Given by value, use Shell.orbital_numbers for convenience
    :ivar spin_direction: expects "+" or "-" representing spin up and down
    :ivar double_angular_momentum: 2*J value (of shell only) e.g. two electrons up give 2*J=2
    :ivar electron_count: number of electrons in the shell

    :cvar orbital_numbers: mapping of orbital letters to numbers
    :cvar orbital_letters: inverse mapping to orbital numbers
    :cvar spin_direction_sign: mapping from "-" to -1 and "+" to 1
    """

    def __init__(self, n, l, spin_direction,
                 double_angular_momentum, electron_count):  # type: (int, int, str, int, int) -> None
        """
        Initialize it based on quantum numbers spin and electron count. Consider using
        a factory method create from string for convenience.
        :param n: Starting from 1
        :param l: Given by value, use Shell.orbital_numbers for convenience
        :param spin_direction: expects "+" or "-" representing spin up and down
        :param double_angular_momentum: 2*J value (of shell only) e.g. two electrons up give 2*J=2
        :param electron_count: number of electrons in the shell
        """
        self.n = n
        self.l = l
        self.spin_direction = spin_direction
        self.double_angular_momentum = double_angular_momentum
        self.electron_count = electron_count

        self.__assert_state_is_fine(), "Invalid shell configuration {}".format(str(self))

    def __repr__(self):  # type: () -> str
        return str(self.n) + \
               self.orbital_letters[self.l] + \
               self.spin_direction + \
               str(self.electron_count) + \
               "(" + str(self.double_angular_momentum) + ")"

    def __eq__(self, other):  # type: (Shell, Shell) -> bool
        return str(self) == str(other)

    def __ne__(self, other):  # type: (Shell, Shell) -> bool
        return not self == other

    def get_latex_repr(self):  # type: () -> str
        """
        Method to generate shell representation in latex format
        :return: Representation of Shell analogous to "$[2p+]^4_0$"
        """
        return "$[{}{}{}]^{}_{}$".format(
            self.n,
            self.orbital_letters[self.l],
            self.spin_direction,
            self.electron_count,
            self.double_angular_momentum
        )

    def is_full(self):
        """
        Returns true if there is maximum number of electrons in the shell
        :return:
        """
        return self.electron_count == self.__get_max_electron_count()

    def __get_max_electron_count(self):
        j2 = 2 * self.l + Shell.spin_direction_sign[self.spin_direction]
        return j2 + 1

    def __get_max_double_angular_momentum(self):
        return 2 * self.l + self.__get_max_electron_count()

    @staticmethod
    def create_from_string(shell_repr):  # type: (str) -> Shell
        """
        Factory method to deconstruct a string of form 3d+4(2) and create a Shell instance based on it
        :param shell_repr: string to deconstruct
        :return: instance of Shell
        """
        orbitals = reduce(lambda string_so_far, orbital: string_so_far + orbital, Shell.orbital_letters.itervalues())
        pattern = re.compile(r"^\d[" + orbitals + r"][+-]\d\(\d\)$")
        assert pattern.match(shell_repr) is not None, "Invalid string to generate shell {}".format(shell_repr)

        return Shell(
            n=int(shell_repr[0]),
            l=Shell.orbital_numbers[shell_repr[1]],
            spin_direction=shell_repr[2],
            double_angular_momentum=int(shell_repr[5]),
            electron_count=int(shell_repr[3])
        )

    orbital_numbers = {"s": 0, "p": 1, "d": 2, "f": 3, "g": 4, "h": 5, "i": 6}
    orbital_letters = {number: letter for letter, number in orbital_numbers.iteritems()}
    spin_direction_sign = {"+": 1, "-": -1}

    def __assert_state_is_fine(self):
        assert self.n > 0, \
            "Principal quantum number (n) must be positive in {}".format(self)
        assert abs(self.l) < self.n, \
            "Absolute value of orbital quantum number must be smaller than principal quantum number in {}".format(self)
        assert self.spin_direction == "+" or self.spin_direction == "-", \
            "Spin direction must be either + or - in {}".format(self)
        assert self.electron_count <= self.__get_max_electron_count(), \
            "Electron count must be less or equal to {} in shell {}".format(self.__get_max_electron_count(), self)
        assert self.double_angular_momentum <= self.__get_max_double_angular_momentum(), \
            "Double angular momentum must be less or equal to {} in shell {}".format(
                self.__get_max_double_angular_momentum(), self)


class EnergyLevel:
    """
        Comparable class representing a single energy level.

        :ivar configuration: list of terms representing the full energy level configuration
    """

    def __init__(self, configuration):  # type: (list) -> None
        """
        Init using list of instances of LevelTerm representing the whole configuration
        :param configuration: list of LevelTerm instances
        """
        self.configuration = configuration

    def __repr__(self):  # type: () -> str
        return " ".join(map(lambda term: str(term.shell) + str(term.j2), self.configuration))

    def __eq__(self, other):  # type: (EnergyLevel, EnergyLevel) -> bool
        return str(self) == str(other)

    def __ne__(self, other):  # type: (EnergyLevel, EnergyLevel) -> bool
        return not self == other

    def get_fac_style_configuration(self):  # type: () -> str
        """
        Returns configuration with following notation 1[s+]2 2[p-]1 meaning 2 electrons in 1s+ and 1 in 2p-
        :return: String of terms separated by space
        """

        def __generate_fac_string(term):  # type: (LevelTerm) -> str
            shell = term.shell
            return "{}[{}{}]{}".format(
                shell.n,
                Shell.orbital_letters[shell.l],
                shell.spin_direction,
                shell.electron_count
            )

        return " ".join(map(__generate_fac_string, self.configuration))

    @staticmethod
    def create_from_string(energy_level_repr):  # type: (str) -> EnergyLevel
        """
        Factory method deconstructing a string 2s+1(1)1.3d+3(3)4 into terms then generating closed configuration
        up to last term and then replacing the proper terms in this configuration with relevant terms
        :param energy_level_repr: string to deconstruct
        :return: EnergyLevel instance
        """
        return EnergyLevel(configuration=map(lambda term_string: LevelTerm(
            shell=Shell.create_from_string(term_string[:-1]),
            j2=term_string[-1]
        ), energy_level_repr.split(" ")))

    def get_fac_repr(self):
        """
        Returns a string of terms separated by dot. The terms are string representations of LevelTerm. Only terms
        with shells that are not full are listed
        :return:
        """
        return ".".join(map(lambda term: str(term), filter(lambda term: not term.shell.is_full(), self.configuration)))


class Transition:
    """
    A class representing a Transition between two energy levels in a specific atom.

    :ivar weighted_oscillator_strength: The weighted oscillator strength of the transition gf
    """

    def __init__(self, atom, lower, upper):  # type: (str, EnergyLevel, EnergyLevel) -> None
        """
        Init using the the name of the atom given by string, eg. "Fe" and upper and lower EnergyLevel instances
        :param atom: atom name such as Fe, Ge etc.
        :param lower: lower energy level
        :param upper: upper energy level
        """
        self.lower = lower
        self.upper = upper
        self.atom = atom
        self.weighted_oscillator_strength = self.__get_weighted_oscillator_strength()

    def __indexes_match_self(self, levels, lower_index, upper_index):
        lower = levels[self.lower.get_fac_repr()]
        upper = levels[self.upper.get_fac_repr()]

        return lower == lower_index and upper == upper_index

    def __parse_oscillator_strength(self):  # type: () -> float
        with fac_helpers.Parser(self.atom, self.lower, self.upper) as fac_parser:
            for lower_index, upper_index, strength in fac_parser.structure:
                if self.__indexes_match_self(
                        levels=fac_parser.levels,
                        lower_index=lower_index,
                        upper_index=upper_index
                ):
                    return strength

        raise Exception("Failed to find transition!")

    def __get_weighted_oscillator_strength(self):
        return self.__parse_oscillator_strength()
