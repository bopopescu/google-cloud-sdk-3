# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Implementation of gcloud genomics variants list.
"""

from googlecloudsdk.api_lib import genomics as lib
from googlecloudsdk.api_lib.genomics import genomics_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.third_party.apitools.base.py import list_pager


class List(base.ListCommand):
  """Lists variants that match the search criteria.
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('--limit-calls',
                        type=int,
                        help=('The maximum number of calls to return.'
                              'At least one variant will be returned even '
                              'if it exceeds this limit.'))
    parser.add_argument('--variant-set-id',
                        type=str,
                        help=('Restrict the list to variants in this variant '
                              'set. If omitted, a call set id must be included '
                              'in the request.'))
    parser.add_argument('--call-set-ids',
                        type=arg_parsers.ArgList(min_length=1),
                        default=[],
                        help=('Restrict the list to variants which have calls '
                              'from the listed call sets. If omitted, a '
                              '--variant-set-id must be specified.'))
    parser.add_argument('--reference-name',
                        type=str,
                        required=True,
                        help='Only return variants in this reference sequence.')
    parser.add_argument('--start',
                        type=long,
                        help=('The beginning of the window (0-based '
                              'inclusive) for which overlapping variants '
                              'should be returned. If unspecified, defaults '
                              'to 0.'))
    parser.add_argument('--end',
                        type=long,
                        help=('The end of the window (0-based exclusive) for '
                              'which variants should be returned. If '
                              'unspecified or 0, defaults to the length of the '
                              'reference.'))
    base.PAGE_SIZE_FLAG.SetDefault(parser, 512)

  def Collection(self):
    return 'genomics.variants'

  def RewriteError(self, msg):
    return (msg.replace('variantSetIds', '--variant-set-id')
            .replace('callSetIds', '--call-set-ids')
            .replace('referenceName', '--reference-name')
            .replace('start', '--start')
            .replace('end', '--end'))

  @genomics_util.ReraiseHttpException
  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace, All the arguments that were provided to this
        command invocation.

    Returns:
      A list of variants that meet the search criteria.
    """
    genomics_util.ValidateLimitFlag(args.limit_calls, 'limit-calls')

    apitools_client = self.context[lib.GENOMICS_APITOOLS_CLIENT_KEY]
    messages = self.context[lib.GENOMICS_MESSAGES_MODULE_KEY]
    fields = genomics_util.GetQueryFields(self.GetReferencedKeyNames(args),
                                          'variants')
    if fields:
      global_params = messages.StandardQueryParameters(fields=fields)
    else:
      global_params = None

    variant_set_id = [args.variant_set_id] if args.variant_set_id else []
    pager = list_pager.YieldFromList(
        apitools_client.variants,
        messages.SearchVariantsRequest(
            variantSetIds=variant_set_id,
            callSetIds=args.call_set_ids,
            referenceName=args.reference_name,
            start=args.start,
            end=args.end,
            maxCalls=args.limit_calls),
        global_params=global_params,
        limit=args.limit,
        method='Search',
        batch_size_attribute='pageSize',
        batch_size=args.page_size,
        field='variants')
    return genomics_util.ReraiseHttpExceptionPager(pager, self.RewriteError)
