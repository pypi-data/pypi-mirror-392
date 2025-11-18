import string

nums = string.digits
letts = string.ascii_lowercase + string.ascii_uppercase

class Converter:
    def __init__(self):
        self.converted = ""

    def convert_text(self, text: str):
        self.converted = ""

        for char in text:

            if char in letts:
                index = letts.index(char) + 1
                if index >= len(letts):
                    leter = char
                else:
                    leter = letts[index]
                self.converted += leter
            else:
                pass

            if char in nums:
                index = nums.index(char) + 1
                if index >= len(nums):
                    num = char
                else:
                    num = nums[index]
                self.converted += num
            else:
                pass

        return self.converted