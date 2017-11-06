本次实验中将实现一个全自动的多人会话记录器，该记录器的功能是：在一个多人进行对话的场合中（假设环境噪音很小），自动记录所有谈话内容，并且识别出该场景 中一共有多少人参与谈话，分析出每个人说话的音频片段，并将说话的音频内容自动转成文本内容（中文或英文皆可），最后将所有谈话记录输出成文本对话。
例如，输出内容可能如 下：   
	TalkerA: Have you watched the NBA match last night? It was incredible. What a big win!   
	TalkerB: Yeah, best of the year.   
	TalkerC: I missed that match, but I will watch the replay today.   
	TalkerB: You must. It was awesome.   
	TalkerA: No wonder they could win the champion last year.   
	TalkerC: Alright. I will do it.   
由于该实验涉及多个部分，包括音频自动分段、话者人数估计、话者识别、音频转文本等。本实验要求是离线完成以上各项操作，即会话片段已提前录制完成并作为输入。有兴趣的同学可以选择在线完成以上操作，即随着谈话的进行而实时的识别出话者并将其谈话内容实时的转成文本，谈话结束后，所有谈话内容即生成完毕。 

============================================================================================================================================================================

audio.wav是我们提供的音频材料，包含两人的对话内容。
AudioNote User Guide.pdf中介绍了软件的使用方法。
AudioNote文档.pdf是我们最终的说明文档。
AudioNote文件夹中是工程的源码