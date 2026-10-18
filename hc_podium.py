"""Meshy AI text-to-3D podium conversion WITHHELD after Blender visual QA.

The downloaded model has a detached metal piece floating beside the podium,
visible in the Meshy thumbnail and our front/BG3/rear previews. Batch rules
prohibit shipping broken geometry. Diagnostics live under work/podium/.
UNVERIFIED in game: all behavior; this generator deliberately writes nothing.
"""


def generate_podium(public_dir, add_loca, get_guid):
    """Reject the broken source before writing assets, stats or spell patches."""
    raise ValueError('HC_CouncilPodium withheld: Meshy source has a floating detached '
                     'metal part; see work/podium-report.md. Replace or repair the '
                     'source model and repeat visual QA before enabling this prop.')
