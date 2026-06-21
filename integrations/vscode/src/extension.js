const vscode = require("vscode");
const cp = require("child_process");
const fs = require("fs");
const path = require("path");

let output;

function workspaceRoot() {
  const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  return folder ? folder.uri.fsPath : process.cwd();
}

function cliArgs(extra) {
  const config = vscode.workspace.getConfiguration("sephirot");
  return ["-m", config.get("cliModule", "sephirot.cli"), ...extra];
}

function runCli(extra, options = {}) {
  const config = vscode.workspace.getConfiguration("sephirot");
  const pythonPath = config.get("pythonPath", "python3");
  const cwd = options.cwd || workspaceRoot();
  output.show(true);
  output.appendLine(`$ ${pythonPath} ${cliArgs(extra).join(" ")}`);
  const result = cp.spawnSync(pythonPath, cliArgs(extra), {
    cwd,
    encoding: "utf8",
    env: process.env
  });
  if (result.stdout) {
    output.append(result.stdout);
  }
  if (result.stderr) {
    output.append(result.stderr);
  }
  if (result.status !== 0) {
    vscode.window.showErrorMessage(`Sephirot command failed with exit ${result.status}`);
  }
  return result;
}

async function newSeed() {
  const context = await vscode.window.showInputBox({
    prompt: "Malkuth current state -> Kether target state",
    placeHolder: "Sales representative -> revenue leader"
  });
  if (context === undefined) {
    return;
  }
  const out = path.join(workspaceRoot(), "sephirot.seed.json");
  runCli(["new", "--context", context, "--out", out]);
  vscode.window.showInformationMessage(`Created ${out}`);
}

async function newFromTemplate() {
  const template = await vscode.window.showQuickPick(
    [
      { label: "agent-runtime", description: "Hermes/Ouroboros-style agent framework" },
      { label: "succession-agent", description: "Tacit expertise to reproducible capability" }
    ],
    { placeHolder: "Select a Sephirot domain ontology template" }
  );
  if (!template) {
    return;
  }
  const out = path.join(workspaceRoot(), "sephirot.seed.json");
  runCli(["template", "--name", template.label, "--out", out]);
  vscode.window.showInformationMessage(`Created ${out}`);
}

function profile() {
  runCli(["profile"]);
}

function validate() {
  runCli(["validate", "--input", "sephirot.seed.json"]);
}

function plan() {
  runCli(["plan", "--input", "sephirot.seed.json"]);
}

function score() {
  runCli(["score", "--input", "sephirot.seed.json"]);
}

function build() {
  runCli(["build", "--input", "sephirot.seed.json", "--out", "sephirot.graph.json"]);
}

function visualize() {
  const root = workspaceRoot();
  const graph = path.join(root, "sephirot.graph.json");
  const seed = path.join(root, "sephirot.seed.json");
  const input = fs.existsSync(graph) ? "sephirot.graph.json" : "sephirot.seed.json";
  if (!fs.existsSync(graph) && !fs.existsSync(seed)) {
    vscode.window.showErrorMessage("No sephirot.graph.json or sephirot.seed.json found");
    return;
  }
  runCli(["visualize", "--input", input, "--format", "html", "--out", "sephirot.graph.html"]);
}

function exportNeo4j() {
  runCli(["export-neo4j", "--input", "sephirot.graph.json", "--out", "sephirot.cypher"]);
}

function exportGraphml() {
  runCli(["export-graphml", "--input", "sephirot.graph.json", "--out", "sephirot.graphml"]);
}

async function exportRdf() {
  const format = await vscode.window.showQuickPick(
    [
      { label: "turtle", description: "Write sephirot.ttl" },
      { label: "jsonld", description: "Write sephirot.jsonld" }
    ],
    { placeHolder: "Select ontology export format" }
  );
  if (!format) {
    return;
  }
  const out = format.label === "jsonld" ? "sephirot.jsonld" : "sephirot.ttl";
  runCli(["export-rdf", "--input", "sephirot.graph.json", "--format", format.label, "--out", out]);
}

function doctor() {
  runCli(["doctor"]);
}

function activate(context) {
  output = vscode.window.createOutputChannel("Sephirot");
  context.subscriptions.push(output);
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.profile", profile));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.newSeed", newSeed));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.newFromTemplate", newFromTemplate));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.validate", validate));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.plan", plan));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.score", score));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.build", build));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.visualize", visualize));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.exportNeo4j", exportNeo4j));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.exportRdf", exportRdf));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.exportGraphml", exportGraphml));
  context.subscriptions.push(vscode.commands.registerCommand("sephirot.doctor", doctor));
}

function deactivate() {}

module.exports = { activate, deactivate };
