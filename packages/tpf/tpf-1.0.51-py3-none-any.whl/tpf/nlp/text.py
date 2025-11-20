
import jieba     
import pandas as pd 


class Word:
    def __init__(self) -> None:
        self.jieba = jieba 
        

    @staticmethod
    def add_jieba_dict(data=None, cols=[], save_path=None):
        """追加列的不重复值到jieba字典
        """
        # 将labels写入save_path文件，一行一个label，后续作为jieba自定义单词字典使用
        if cols and len(cols)>0:
            labels = []
            for lb in cols:
                ll = data[lb].unique().tolist()
                labels.extend(ll)

            # 写入labels到文件，一行一个label
            if save_path:
                # 读取现有文件内容
                existing_labels = set()
                try:
                    with open(save_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                existing_labels.add(line)
                    print(f"从{save_path}读取了{len(existing_labels)}个现有labels")
                except FileNotFoundError:
                    print(f"{save_path}不存在，将创建新文件")

                # 合并并去重
                all_labels = set(labels) | existing_labels

                # 覆盖式写入文件
                with open(save_path, 'w', encoding='utf-8') as f:
                    for label in sorted(all_labels):
                        f.write(str(label) + '\n')
                print(f"已将{len(all_labels)}个去重后的labels写入{save_path}（新增{len(set(labels) - existing_labels)}个）")
                jieba.load_userdict(save_path)
        elif save_path:   
            jieba.load_userdict(save_path)
        

class NLP:
    def __init__(self):
        self.t5_model = None 
        self.t5_tokenizer = None 
        self.t5_device = 'cpu'

    def init_t5(self, model_name = '/wks/models/t5_summary_en_ru_zh_base_2048', device = 'cpu'):
        self.t5_device = device
        from modelscope import T5ForConditionalGeneration, T5Tokenizer
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        model.eval()
        model.to(device)
        generation_config = model.generation_config
        # for quality generation
        generation_config.length_penalty = 0.6
        generation_config.no_repeat_ngram_size = 2
        generation_config.num_beams = 10
        
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.t5_tokenizer = tokenizer 
        self.t5_model = model
        self.t5_generation_config = generation_config
        
        return tokenizer,model,generation_config
    def summary_t5(self, text):
        if self.t5_model is None:
            self.init_t5()
        # text summary generate
        prefix = 'summary to zh: '
        src_text = prefix + text
        input_ids = self.t5_tokenizer(src_text, return_tensors="pt")
        
        generated_tokens = self.t5_model.generate(**input_ids.to(self.t5_device), generation_config=generation_config)
        
        result = self.t5_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return result


# 尝试导入pyhanlp，如果未安装则设为None
try:
    from pyhanlp import HanLP
    PYHANLP_AVAILABLE = True
except ImportError:
    HanLP = None
    PYHANLP_AVAILABLE = False


class TLP:
    def __init__(self) -> None:
        
        pass 
    
    @staticmethod
    def cut_words(text):
        """使用结巴分词对文本进行分词
        """
        words = jieba.cut(text, cut_all=False)
        return words 
    
    @staticmethod
    def summary(text, n=5):
        """使用HanLP进行文本摘要

        Args:
            text (str): 待摘要的文本
            n (int): 返回的摘要数量

        Returns:
            list: 摘要列表，如果pyhanlp未安装则返回空列表
        """
        if not PYHANLP_AVAILABLE:
            print("警告: pyhanlp未安装，无法使用HanLP进行文本摘要")
            return []

        try:
            # 使用HanLP进行摘要
            summary_result = HanLP.extractSummary(text, n)
            return [str(item) for item in summary_result]
        except Exception as e:
            print(f"HanLP摘要失败: {e}")
            return []

    @staticmethod
    def segment(text):
        """使用HanLP进行分词

        Args:
            text (str): 待分词的文本

        Returns:
            list: 分词结果，如果pyhanlp未安装则返回空列表
        """
        if not PYHANLP_AVAILABLE:
            print("警告: pyhanlp未安装，无法使用HanLP进行分词")
            return []

        try:
            # 使用HanLP进行分词
            segment_result = HanLP.segment(text)
            return [str(item) for item in segment_result]
        except Exception as e:
            print(f"HanLP分词失败: {e}")
            return [] 