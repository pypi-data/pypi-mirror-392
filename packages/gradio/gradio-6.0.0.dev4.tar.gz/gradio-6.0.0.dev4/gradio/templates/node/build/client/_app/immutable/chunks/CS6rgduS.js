import "./9B4_veAf.js";
import { p as push, M as user_effect, o as pop } from "./DEzry6cj.js";
import { r as rest_props } from "./DUftb7my.js";
import { G as Gradio } from "./DZzBppkm.js";
function Index($$anchor, $$props) {
  push($$props, true);
  let props = rest_props($$props, ["$$slots", "$$events", "$$legacy"]);
  const gradio = new Gradio(props);
  user_effect(() => {
    gradio.props.value && gradio.dispatch("change");
  });
  pop();
}
export {
  Index as default
};
//# sourceMappingURL=CS6rgduS.js.map
