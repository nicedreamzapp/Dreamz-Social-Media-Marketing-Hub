/* Reddit ChatGPT Integration - Platform-Specific Prompts and Logic
* Handles Reddit-specific prompt templates and initialization
* Requires chatgpt_core.js to be loaded first
*/

class RedditChatGPT {
   constructor() {
       this.promptTemplates = {
           'discussion': `Before creating a Reddit post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create a discussion-focused Reddit post (300-400 words) that starts a genuine conversation about the product. Focus on asking questions, sharing experiences, and encouraging community input. Keep it authentic and non-promotional while highlighting the benefits I identified. Include relevant technical details that Reddit users appreciate.

Product Information:
{product_text}`,

           'review': `Before creating a Reddit post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create an honest Reddit review post (300-400 words) that reads like a genuine user experience. Include pros and cons, detailed observations, and practical insights based on the features I identified. Write in a conversational tone that feels authentic to Reddit's community culture.

Product Information:
{product_text}`,

           'educational': `Before creating a Reddit post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create an educational Reddit post (300-400 words) that teaches the community something valuable about this type of product. Focus on technical details, best practices, and helpful tips based on the features I identified. Make it informative and useful for both beginners and experienced users.

Product Information:
{product_text}`
       };
   }

   init(productData) {
       if (!window.ChatGPTCore) {
           console.error('ChatGPT Core not found. Make sure chatgpt_core.js is loaded first.');
           return;
       }
       
       window.ChatGPTCore.init(productData);
       console.log('Reddit ChatGPT integration initialized');
   }

   openChatGPT(promptType) {
       if (!window.ChatGPTCore) {
           console.error('ChatGPT Core not available');
           return;
       }

       const promptTemplate = this.promptTemplates[promptType];
       if (!promptTemplate) {
           console.error('Invalid Reddit prompt type:', promptType);
           return;
       }

       window.ChatGPTCore.openPrompt(promptTemplate, promptType, 'caption-text');
   }
}

// Initialize global instance
window.RedditChatGPT = new RedditChatGPT();

// Global function for template compatibility
function openChatGPT(promptType) {
   window.RedditChatGPT.openChatGPT(promptType);
}

