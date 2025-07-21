/** Create a reactive props proxy to allow updating of props. */
export function updateable_props<T extends Record<string, unknown>>(
  raw_props: T,
): [props: T, update: (v: T) => void] {
  // Use shallow reactivity to avoid unnecessary overhead from deep watching
  const props = $state.raw(raw_props);
  return [
    props,
    (new_props) => {
      Object.assign(props, new_props);
    },
  ];
}
