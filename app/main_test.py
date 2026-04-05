"""Minimal test version of Nyaya Sahayak to diagnose crash."""
import gradio as gr

def build_app():
    with gr.Blocks(title="Nyaya Test") as demo:
        gr.Markdown("# Test App")
        
        with gr.Column(visible=True) as col1:
            gr.Markdown("Welcome")
            btn = gr.Button("Click me")
        
        with gr.Column(visible=False) as col2:
            gr.Markdown("Hidden")
        
        def on_click():
            return gr.update(visible=False), gr.update(visible=True)
        
        btn.click(on_click, outputs=[col1, col2])
    
    return demo

def main():
    demo = build_app()
    demo.launch()

if __name__ == "__main__":
    main()
