import google.generativeai as genai

# 填入你的真实 API KEY
genai.configure(api_key="这里填你的KEY") 

print("开始测试 Imagen 出图权限...")
try:
    model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    result = model.generate_images(prompt="A red Haval SUV in desert", number_of_images=1, aspect_ratio="16:9")
    print("✅ 恭喜！权限完全正常，图已经成功生成在内存里了！")
except Exception as e:
    print(f"❌ 权限或网络被卡脖子了，核心死因如下：\n{e}")
