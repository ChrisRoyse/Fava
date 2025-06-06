<script lang="ts">
  import { timeDay } from "d3-time";

  import { account_details } from "../stores";
  import { uptodate_indicator_grey_lookback_days } from "../stores/fava_options";

  interface Props {
    /** The account name. */
    account: string;
    /** Whether the indicator should be slightly smaller for the tree tables. */
    small?: boolean;
  }

  let { account, small = false }: Props = $props();

  let details = $derived($account_details[account]);
  let status = $derived(details?.uptodate_status);
  let balance = $derived(details?.balance_string ?? "");
  let last_entry = $derived(details?.last_entry);

  let last_account_activity = $derived(
    last_entry ? timeDay.count(last_entry.date, new Date()) : 0,
  );
</script>

{#if status}
  {#if status === "green"}
    <span
      class="status-indicator status-green"
      class:small
      title="The last entry is a passing balance check."
    ></span>
  {:else}
    <copyable-text
      class="status-indicator status-{status}"
      class:small
      title={`${
        status === "yellow"
          ? "The last entry is not a balance check."
          : "The last entry is a failing balance check."
      }

Click to copy the balance directives to the clipboard:

${balance}`}
      data-clipboard-text={balance}
    ></copyable-text>
  {/if}
  {#if last_account_activity > $uptodate_indicator_grey_lookback_days}
    <span
      class="status-indicator status-gray"
      class:small
      title="This account has not been updated in a while. ({last_account_activity} days ago)"
    ></span>
  {/if}
{/if}

<style>
  .status-indicator {
    width: 10px;
    height: 10px;
    margin: 0 0 0 10px;
    border-radius: 10px;
  }

  .status-indicator.small {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin: 5px;
    border-radius: 6px;
  }

  .status-indicator.status-gray {
    margin-left: 0;
  }
</style>
