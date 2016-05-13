# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Flags and helpers for the compute backend-services backend commands."""

from googlecloudsdk.command_lib.compute import flags


def AddDescription(parser):
  parser.add_argument(
      '--description',
      help='An optional, textual description for the backend.')


def AddInstanceGroup(parser, multizonal=False):
  """Add arguments to define instance group."""
  g = parser.add_mutually_exclusive_group(required=True)

  g.add_argument(
      '--group',
      help=('The name of the legacy instance group '
            '(deprecated resourceViews API) that will receive the traffic. '
            'Use --instance-group flag instead.'))

  g.add_argument(
      '--instance-group',
      help=('The name or URI of a Google Cloud Instance Group that can receive'
            ' traffic.'))

  scope_parser = parser
  if multizonal:
    scope_parser = parser.add_mutually_exclusive_group()
    flags.AddRegionFlag(
        scope_parser,
        resource_type='instance group',
        operation_type='add to the backend service')
  flags.AddZoneFlag(
      scope_parser,
      resource_type='instance group',
      operation_type='add to the backend service')


def AddBalancingMode(parser):
  balancing_mode = parser.add_argument(
      '--balancing-mode',
      choices=['RATE', 'UTILIZATION'],
      type=lambda x: x.upper(),
      help='Defines the strategy for balancing load.')
  balancing_mode.detailed_help = """\
      Defines the strategy for balancing load. ``UTILIZATION'' will
      rely on the CPU utilization of the instances in the group when
      balancing load. When using ``UTILIZATION'',
      ``--max-utilization'' can be used to set a maximum target CPU
      utilization for each instance. ``RATE'' will spread load based on
      how many requests per second (RPS) the group can handle. There
      are two ways to specify max RPS: ``--max-rate'' which defines
      the max RPS for the whole group or ``--max-rate-per-instance'',
      which defines the max RPS on a per-instance basis.

      In ``UTILIZATION'', you can optionally limit based on RPS in
      addition to CPU by setting either ``--max-rate-per-instance'' or
      ``--max-rate''.
      """


def AddMaxUtilization(parser):
  max_utilization = parser.add_argument(
      '--max-utilization',
      type=float,
      help=('The target CPU utilization of the group as a '
            'float in the range [0.0, 1.0].'))
  max_utilization.detailed_help = """\
      The target CPU utilization for the group as a float in the range
      [0.0, 1.0]. This flag can only be provided when the balancing
      mode is ``UTILIZATION''.
      """


def AddRate(parser):
  rate_group = parser.add_mutually_exclusive_group()

  rate_group.add_argument(
      '--max-rate',
      type=int,
      help='Maximum requests per second (RPS) that the group can handle.')

  rate_group.add_argument(
      '--max-rate-per-instance',
      type=float,
      help='The maximum per-instance requests per second (RPS).')


def AddCapacityScalar(parser):
  capacity_scaler = parser.add_argument(
      '--capacity-scaler',
      type=float,
      help=('A float in the range [0, 1.0] that scales the maximum '
            'parameters for the group (e.g., max rate).'))
  capacity_scaler.detailed_help = """\
      A float in the range [0, 1.0] that scales the maximum
      parameters for the group (e.g., max rate). A value of 0.0 will
      cause no requests to be sent to the group (i.e., it adds the
      group in a ``drained'' state). The default is 1.0.
      """
