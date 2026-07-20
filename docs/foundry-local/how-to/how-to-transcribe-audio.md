    
# Transcribe recorded audio files with Foundry Local

Use Foundry Local's native audio transcription API and convert a local audio file into text. In this article, you create a console application that downloads a Whisper model, loads it, and streams transcription output.

::: zone pivot="programming-language-csharp"

## Prerequisites

- [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) or later installed.

## Samples repository

The complete sample code for this article is available in the [foundry-samples GitHub repository](https://github.com/microsoft-foundry/foundry-samples). To clone the repository and navigate to the sample use:

```bash
git clone https://github.com/microsoft-foundry/foundry-samples.git
cd foundry-samples/samples/csharp/foundry-local/audio-transcription-example
```

## Install packages


If you're developing or shipping on Windows, select the **Windows** tab. The Windows package integrates with the [Windows ML](/windows/ai/new-windows-ml/overview) runtime — it provides the same API surface area with a wider breadth of hardware acceleration.

### [Windows](#tab/windows)

```bash
dotnet add package Microsoft.AI.Foundry.Local.WinML
dotnet add package OpenAI
```

### [Cross-Platform](#tab/xplatform)

```bash
dotnet add package Microsoft.AI.Foundry.Local
dotnet add package OpenAI
```

---

The C# samples in the GitHub repository are preconfigured projects. If you're building from scratch, you should read the [Foundry Local SDK reference](../reference/reference-sdk-current.md) for more details on how to set up your C# project with Foundry Local. 


## Transcribe an audio file

Copy and paste the following code into a C# file named `Program.cs`:

:::code language="csharp" source="~/foundry-local-main/samples/csharp/foundry-local/audio-transcription-example/Program.cs" id="complete_code":::

The sample includes a `Recording.mp3` file. To transcribe a different audio file, pass the file path as an argument.

```bash
dotnet run
```

To transcribe a custom audio file:

```bash
dotnet run -- path/to/audio.mp3
```

::: zone-end
::: zone pivot="programming-language-javascript"

## Prerequisites

- [Node.js](https://nodejs.org/en/download/) version 20 or later installed.

## Samples repository

The complete sample code for this article is available in the [foundry-samples GitHub repository](https://github.com/microsoft-foundry/foundry-samples). To clone the repository and navigate to the sample use:

```bash
git clone https://github.com/microsoft-foundry/foundry-samples.git
cd foundry-samples/samples/javascript/foundry-local/audio-transcription-example
```

## Install packages


If you're developing or shipping on Windows, select the **Windows** tab. The Windows package integrates with the [Windows ML](/windows/ai/new-windows-ml/overview) runtime — it provides the same API surface area with a wider breadth of hardware acceleration.

### [Windows](#tab/windows)

```bash
npm install foundry-local-sdk-winml openai
```

### [Cross-Platform](#tab/xplatform)

```bash
npm install foundry-local-sdk openai
```

---


## Transcribe an audio file

Copy and paste the following code into a JavaScript file named `app.js`:

:::code language="javascript" source="~/foundry-local-main/samples/javascript/foundry-local/audio-transcription-example/app.js" id="complete_code":::

The sample includes a `Recording.mp3` file. To transcribe a different audio file, pass the file path as an argument.

To run the application, use the following command in your terminal:

```bash
node app.js
```

To transcribe a custom audio file:

```bash
node app.js path/to/audio.mp3
```

::: zone-end
::: zone pivot="programming-language-python"

## Prerequisites

- [Python 3.11](https://www.python.org/downloads/) or later installed.

## Samples repository

The complete sample code for this article is available in the [foundry-samples GitHub repository](https://github.com/microsoft-foundry/foundry-samples). To clone the repository and navigate to the sample use:

```bash
git clone https://github.com/microsoft-foundry/foundry-samples.git
cd foundry-samples/samples/python/foundry-local/audio-transcription
```

## Install packages


If you're developing or shipping on Windows, select the **Windows** tab. The Windows package integrates with the [Windows ML](/windows/ai/new-windows-ml/overview) runtime — it provides the same API surface area with a wider breadth of hardware acceleration.

### [Windows](#tab/windows)

```bash
pip install foundry-local-sdk-winml openai
```

### [Cross-Platform](#tab/xplatform)

```bash
pip install foundry-local-sdk openai
```

---


## Transcribe an audio file

Copy and paste the following code into a Python file named `app.py`:

:::code language="python" source="~/foundry-local-main/samples/python/foundry-local/audio-transcription/src/app.py" id="complete_code":::

The sample includes a `Recording.mp3` file. To transcribe a different audio file, pass the file path as an argument.

Run the code by using the following command:

```bash
python app.py
```

To transcribe a custom audio file:

```bash
python app.py path/to/audio.mp3
```

::: zone-end
::: zone pivot="programming-language-rust"

## Prerequisites

- [Rust and Cargo](https://www.rust-lang.org/tools/install) installed (Rust 1.70.0 or later).

## Samples repository

The complete sample code for this article is available in the [foundry-samples GitHub repository](https://github.com/microsoft-foundry/foundry-samples). To clone the repository and navigate to the sample use:

```bash
git clone https://github.com/microsoft-foundry/foundry-samples.git
cd foundry-samples/samples/rust/foundry-local/audio-transcription-example
```

## Install packages


If you're developing or shipping on Windows, select the **Windows** tab. The Windows package integrates with the [Windows ML](/windows/ai/new-windows-ml/overview) runtime — it provides the same API surface area with a wider breadth of hardware acceleration.

### [Windows](#tab/windows)

```bash
cargo add foundry-local-sdk --features winml
cargo add tokio --features full
cargo add tokio-stream anyhow
```

### [Cross-Platform](#tab/xplatform)

```bash
cargo add foundry-local-sdk
cargo add tokio --features full
cargo add tokio-stream anyhow
```

---


## Transcribe an audio file

Replace the contents of `main.rs` with the following code:

:::code language="rust" source="~/foundry-local-main/samples/rust/foundry-local/audio-transcription-example/src/main.rs" id="complete_code":::

The sample includes a `Recording.mp3` file. To transcribe a different audio file, pass the file path as an argument.

Run the code by using the following command:

```bash
cargo run
```

To transcribe a custom audio file:

```bash
cargo run -- path/to/audio.mp3
```

::: zone-end

## Related content

- [Use native chat completions API with Foundry Local](how-to-use-native-chat-completions.md)
- [Use chat completions via REST server with Foundry Local](how-to-integrate-with-inference-sdks.md)
- [Use Foundry Local with LangChain](how-to-use-langchain-with-foundry-local.md)
- [Compile Hugging Face models and run on Foundry Local](how-to-compile-hugging-face-models.md)
- [Explore the Foundry Local CLI reference](../reference/reference-cli.md)