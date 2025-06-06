import {
  defineLanguageFacet,
  Language,
  languageDataProp,
  LanguageSupport,
  syntaxHighlighting,
} from "@codemirror/language";
import { highlightTrailingWhitespace, keymap } from "@codemirror/view";
import { styleTags, tags } from "@lezer/highlight";
import { Language as TSLanguage, Parser as TSParser } from "web-tree-sitter";

// Import the new WASM loading and verification function
import { loadAndVerifyWasmModule } from "../generated/pqcWasmConfig"; // Removed getFavaPqcWasmConfig
import ts_wasm from "../../node_modules/web-tree-sitter/tree-sitter.wasm";
import { beancountCompletion } from "./beancount-autocomplete";
import { beancountFold } from "./beancount-fold";
import { beancountFormat } from "./beancount-format";
import { beancountEditorHighlight } from "./beancount-highlight";
import { beancountIndent } from "./beancount-indent";
// The direct import of ts_beancount_wasm might become illustrative if path is fully from config
// import ts_beancount_wasm from "./tree-sitter-beancount.wasm";
import { LezerTSParser } from "./tree-sitter-parser";

/** Import the tree-sitter and Beancount language WASM files and initialise the parser. */
async function loadBeancountParser(): Promise<TSParser> {
  const generalTsWasmPath = import.meta.resolve(ts_wasm);
  await TSParser.init({ locateFile: () => generalTsWasmPath });

  // Fetch and verify the Beancount grammar WASM using the new service
  // This will use the path from PQC configuration (e.g., /assets/tree-sitter-beancount.wasm)
  const beancountWasmBuffer = await loadAndVerifyWasmModule();
  
  // TSLanguage.load can take an ArrayBuffer.
  // The path identifier might not be needed here if the buffer is self-sufficient
  // or if the LezerTSParser handles it.
  // const pqcConfig = await getFavaPqcWasmConfig(); // Not needed
  // const beancountWasmPathForLoading = pqcConfig.wasmModulePath; // Not needed

  // TSLanguage.load expects a Uint8Array when given a buffer, not an ArrayBuffer directly.
  const beancountWasmUint8Array = new Uint8Array(beancountWasmBuffer);
  const lang = await TSLanguage.load(beancountWasmUint8Array);
  const parser = new TSParser();
  parser.setLanguage(lang);
  return parser;
}

const beancountLanguageFacet = defineLanguageFacet();
// Restore the beancountLanguageSupportExtensions array definition
const beancountLanguageSupportExtensions = [
  beancountFold,
  syntaxHighlighting(beancountEditorHighlight),
  beancountIndent,
  keymap.of([{ key: "Control-d", mac: "Meta-d", run: beancountFormat }]),
  beancountLanguageFacet.of({
    autocomplete: beancountCompletion,
    commentTokens: { line: ";" },
    indentOnInput: /^\s+\d\d\d\d/,
  }),
  highlightTrailingWhitespace(),
];

/** The node props that allow for highlighting/coloring of the code. */
const props = [
  styleTags({
    account: tags.className,
    currency: tags.unit,
    date: tags.special(tags.number),
    string: tags.string,
    "BALANCE CLOSE COMMODITY CUSTOM DOCUMENT EVENT NOTE OPEN PAD PRICE TRANSACTION QUERY":
      tags.keyword,
    "tag link": tags.labelName,
    number: tags.number,
    key: tags.propertyName,
    bool: tags.bool,
    "PUSHTAG POPTAG PUSHMETA POPMETA OPTION PLUGIN INCLUDE": tags.standard(
      tags.string,
    ),
  }),
  languageDataProp.add((type) =>
    type.isTop ? beancountLanguageFacet : undefined,
  ),
];

/** Only load the TSParser once. */
let load_parser: Promise<TSParser> | null = null;

/**
 * Get the LanguageSupport for Beancount.
 *
 * Since this might need to load the tree-sitter parser, this is async.
 */
export async function getBeancountLanguageSupport(): Promise<LanguageSupport> {
  load_parser ??= loadBeancountParser();
  const ts_parser = await load_parser;
  return new LanguageSupport(
    new Language(
      beancountLanguageFacet,
      new LezerTSParser(ts_parser, props, "beancount_file"),
      [],
      "beancount",
    ),
    beancountLanguageSupportExtensions,
  );
}
