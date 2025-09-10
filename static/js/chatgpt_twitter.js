/* Twitter ChatGPT Integration - Platform-Specific Prompts and Logic
* Handles Twitter-specific prompt templates and initialization
* Requires chatgpt_core.js to be loaded first
*/

class TwitterChatGPT {
   constructor() {
       this.promptTemplates = {
           'viral': `Before creating a Twitter post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create a viral Twitter post (200-250 characters) that's attention-grabbing, shareable, and likely to get retweets. Use compelling language, create curiosity, and focus on the benefits I identified. Keep it punchy and engaging. Include 1-3 trending hashtags that are relevant to the product.

Product Information:
{product_text}`,

           'promotional': `Before creating a Twitter post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create a promotional Twitter post (200-250 characters) that highlights the product's value and drives sales. Focus on the features and benefits I identified, include a clear call-to-action, and make it compelling for potential buyers. Use professional but engaging language. Include 1-3 relevant hashtags.

Product Information:
{product_text}`,

           'engagement': `Before creating a Twitter post, ask me these 3 short questions:
1. What's the main benefit this product offers users?
2. Is this product better for beginners or experienced users?
3. What's the standout feature that makes this product unique?

After I answer, create an engagement-focused Twitter post (200-250 characters) that encourages replies, likes, and discussion. Ask a question, share a relatable experience, or start a conversation related to the product and benefits I identified. Make it interactive and community-building. Include 1-3 relevant hashtags.

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
       console.log('Twitter ChatGPT integration initialized');
   }

   openChatGPT(promptType) {
       if (!window.ChatGPTCore) {
           console.error('ChatGPT Core not available');
           return;
       }

       const promptTemplate = this.promptTemplates[promptType];
       if (!promptTemplate) {
           console.error('Invalid Twitter prompt type:', promptType);
           return;
       }

       window.ChatGPTCore.openPrompt(promptTemplate, promptType, 'caption-text');
   }
}

// Initialize global instance
window.TwitterChatGPT = new TwitterChatGPT();

// Global function for template compatibility
function openChatGPT(promptType) {
   window.TwitterChatGPT.openChatGPT(promptType);
}

