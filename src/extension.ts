// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { execFile } from 'child_process';

import * as util from 'util';
let execFileP = util.promisify(execFile);

let fileToText: {[s: string]: string} = {};

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "python-ast-preview" is now active!');

    let scheme = "python-ast-preview";
    let virtualDocProvider = new class implements vscode.TextDocumentContentProvider {
        // emitter and its event
        onDidChangeEmitter = new vscode.EventEmitter<vscode.Uri>();
        onDidChange = this.onDidChangeEmitter.event;

        provideTextDocumentContent(uri: vscode.Uri): Thenable<string> {
            // simply invoke cowsay, use uri-path as text
            let config = vscode.workspace.getConfiguration();
            // @ts-ignore
            let pythonPath:string = config.get("python-ast-preview.pythonPath");
            if (pythonPath === null && config.has("python.pythonPath")) {
                // @ts-ignore
                pythonPath = config.get("python.pythonPath");
            }
            else {
                pythonPath = "python";
            }
            console.log("Python path: ", pythonPath);

            let text = fileToText[uri.path]
            delete fileToText[uri.path]

            let helperPython = context.asAbsolutePath('helper.py');
            return execFileP(pythonPath, [helperPython, text]).then(output => output.stdout);
        }
    }
    let docDisposable = vscode.workspace.registerTextDocumentContentProvider(
        scheme, virtualDocProvider);

    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('extension.preview-python-ast', async () => {
        // The code you place here will be executed every time your command is executed
        if (!vscode.window.activeTextEditor) {
            return; // no editor
        }
        let { document } = vscode.window.activeTextEditor;
        if (document.languageId !== "python") {
            console.log("Only python files supported by 'python-preview-ast'");
            return;
        }

        // Display a message box to the user
        let message = document.getText();
        let filename = 'untitled';
        if (!document.isUntitled) {
            filename = document.uri.path;
        }
        let uri = vscode.Uri.parse(scheme + ':' + filename + '.json');
        fileToText[filename + '.json'] = message;

        let doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(
            doc,
            {
                preview: false,
                viewColumn: vscode.ViewColumn.Beside
            }
        );
    });

    context.subscriptions.push(docDisposable);
    context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {}
