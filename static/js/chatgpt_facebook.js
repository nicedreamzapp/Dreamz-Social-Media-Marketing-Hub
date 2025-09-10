/* Facebook ChatGPT Integration - Platform-Specific Prompts and Logic
* Handles Facebook-specific prompt templates and initialization
* Requires chatgpt_core.js to be loaded first
*/

class FacebookChatGPT {
   constructor() {
       this.promptTemplates = {
           'story': `Before creating a Facebook post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced concentrate users?  
3. What's the standout feature that makes this product unique?

After I answer, create a story-driven Facebook business post (200-250 words) that tells a brief story about the product, focuses on the benefits and features I identified, and includes a natural call-to-action. Keep cannabis terminology minimal and professional. Include 3-5 relevant hashtags.

Product Information:
{product_text}`,

           'educational': `Before creating a Facebook post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced concentrate users?
3. What's the standout feature that makes this product unique?

After I answer, create an educational Facebook business post (200-250 words) that teaches something valuable about the product or how to use it effectively. Focus on solving problems or answering common questions. Keep cannabis terminology minimal and professional. Include a helpful call-to-action and 3-5 relevant hashtags.

Product Information:
{product_text}`,

           'community': `Before creating a Facebook post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced concentrate users?
3. What's the standout feature that makes this product unique?

After I answer, create a community-building Facebook post (200-250 words) that encourages engagement and interaction. Ask questions, share relatable experiences, or highlight how this product brings people together. Keep cannabis terminology minimal and professional. Include 3-5 relevant hashtags and encourage comments.

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
       console.log('Facebook ChatGPT integration initialized');
   }

   openChatGPT(promptType) {
       if (!window.ChatGPTCore) {
           console.error('ChatGPT Core not available');
           return;
       }

       const promptTemplate = this.promptTemplates[promptType];
       if (!promptTemplate) {
           console.error('Invalid Facebook prompt type:', promptType);
           return;
       }

       window.ChatGPTCore.openPrompt(promptTemplate, promptType, 'caption-text');
   }
}

// Initialize global instance
window.FacebookChatGPT = new FacebookChatGPT();

// Global function for template compatibility
function openChatGPT(promptType) {
   window.FacebookChatGPT.openChatGPT(promptType);
}

