import re

def get_lick_registers(practice_lick_data, all_licks_from_scale):
    """
    Analyzes a practice lick to determine which registers it uses by
    comparing its notes to the defined scale parts.

    Parameters
    ----------
    practice_lick_data : list
        The 'lick_data' list for the lick being analyzed.
    all_licks_from_scale : list
        The complete list of all lick objects for the current scale,
        where the first three are the low, middle, and high scale parts.

    Returns
    -------
    list
        A sorted list of unique register names used (e.g., ["low", "middle"]).
    """
    if not practice_lick_data or len(all_licks_from_scale) < 3:
        return []

    # Create a set of notes in the practice lick for efficient lookup
    practice_notes = {note['tab'] for note in practice_lick_data}

    # Create sets of notes for each defined scale register
    low_scale_notes = {note['tab'] for note in all_licks_from_scale[0]['lick_data']}
    middle_scale_notes = {note['tab'] for note in all_licks_from_scale[1]['lick_data']}
    high_scale_notes = {note['tab'] for note in all_licks_from_scale[2]['lick_data']}

    found_registers = set()

    # Check for intersection between the practice lick's notes and each register's notes
    if not practice_notes.isdisjoint(low_scale_notes):
        found_registers.add("low")
    if not practice_notes.isdisjoint(middle_scale_notes):
        found_registers.add("middle")
    if not practice_notes.isdisjoint(high_scale_notes):
        found_registers.add("high")

    return sorted(list(found_registers))