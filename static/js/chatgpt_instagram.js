/* Instagram ChatGPT Integration - Platform-Specific Prompts and Logic
 * Handles Instagram-specific prompt templates and initialization
 * Requires chatgpt_core.js to be loaded first
 */

class InstagramChatGPT {
    constructor() {
        this.promptTemplates = {
            'engaging': `Create an engaging Instagram caption for this product that feels natural and authentic.

Requirements:
- Start with a compelling hook (under 125 characters before "...more")
- Use natural line breaks for mobile readability
- Include 8-15 relevant hashtags (mix of niche and popular)
- Keep total under 2,200 characters
- Focus on experience and lifestyle benefits
- Include a natural call-to-action that doesn't talk down to users
- Use 2-4 tasteful emojis maximum

Product Information:
{product_text}

Create a caption that connects with users authentically and highlights what makes this product special without being pushy or condescending.`,

            'lifestyle': `Create a lifestyle-focused Instagram caption for this product that speaks naturally to your audience.

Requirements:
- Start with a relatable lifestyle hook (under 125 characters before "...more")
- Use natural line breaks for mobile readability
- Focus on how this product fits into daily life and personal values
- Create emotional connection through shared experiences
- Include 8-15 lifestyle-appropriate hashtags
- Keep under 2,200 characters
- Use genuine, conversational tone
- Include 2-4 tasteful emojis maximum

Product Information:
{product_text}

Write a caption that feels like it's coming from a real person sharing something they genuinely care about.`,

            'promotional': `Create a promotional Instagram caption for this product that highlights value without being pushy.

Requirements:
- Start with a value-focused hook (under 125 characters before "...more")
- Use natural line breaks for mobile readability
- Highlight key features and benefits naturally
- Create interest through genuine value proposition
- Use professional but approachable language
- Include 8-15 product-specific hashtags
- Include a genuine call-to-action
- Keep under 2,200 characters
- Use 2-4 tasteful emojis maximum

Product Information:
{product_text}

Create a caption that showcases the product's value and benefits while maintaining an authentic, respectful tone.`
        };
    }

    init(productData) {
        if (!window.ChatGPTCore) {
            console.error('ChatGPT Core not found. Make sure chatgpt_core.js is loaded first.');
            return;
        }
        
        window.ChatGPTCore.init(productData);
        window.ChatGPTCore.setPrompts = (prompts) => {
            window.ChatGPTCore.promptTemplates = prompts;
        };
        
        console.log('Instagram ChatGPT integration initialized');
    }

    openChatGPT(promptType) {
        if (!window.ChatGPTCore) {
            console.error('ChatGPT Core not available');
            return;
        }

        const promptTemplate = this.promptTemplates[promptType];
        if (!promptTemplate) {
            console.error('Invalid Instagram prompt type:', promptType);
            return;
        }

        window.ChatGPTCore.openPrompt(promptTemplate, promptType, 'caption-text');
    }
}

// Initialize global instance
window.InstagramChatGPT = new InstagramChatGPT();

// Global function for template compatibility
function openChatGPT(promptType) {
    window.InstagramChatGPT.openChatGPT(promptType);
}

